# -*- coding: utf-8 -*-
# © 2017 FactorLibre - Hugo Santos <hugo.santos@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, exceptions, fields, models, _

import logging

logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    generic_customer_id = fields.Many2one(
        'res.partner', 'Generic Customer',
        help="Set a generic customer for simplified invoice records"
        " to send to SII")


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.multi
    def action_invoice(self):
        inv_ref = self.env['account.invoice']
        inv_line_ref = self.env['account.invoice.line']

        for order in self.browse(self.ids):
            if order.invoice_id:
                continue

            if not order.partner_id:
                raise exceptions.except_orm(
                        _('Error!'),
                        _('Please provide a partner for the sale.'))

            is_refund = order.amount_total < 0
            if not is_refund:
                continue

            acc = order.partner_id.property_account_receivable.id
            inv = {
                'name': order.name,
                'origin': order.name,
                'account_id': acc,
                'journal_id': order.sale_journal.id or None,
                'type': 'out_refund' if is_refund else 'out_invoice',
                'sii_refund_type': 'I' if is_refund else None,
                'reference': order.name,
                'partner_id': order.partner_id.id,
                'comment': order.note or '',
                'currency_id': order.pricelist_id.currency_id.id, # noqa considering partner's sale pricelist's currency
            }
            inv.update(inv_ref.onchange_partner_id(
                'out_invoice', order.partner_id.id)['value'])
            # FORWARDPORT TO SAAS-6 ONLY!
            inv.update({'fiscal_position': False})
            if not inv.get('account_id', None):
                inv['account_id'] = acc
            inv_id = inv_ref.create(inv)

            order.write({'invoice_id': inv_id.id, 'state': 'invoiced'})
            for line in order.lines:
                inv_line = {
                    'invoice_id': inv_id.id,
                    'product_id': line.product_id.id,
                    'quantity': line.qty * -1 if is_refund else line.qty,
                }
                inv_name = line.product_id.name_get()[0][1]
                inv_line.update(inv_line_ref.product_id_change(
                   line.product_id.id,
                   line.product_id.uom_id.id,
                   line.qty,
                   partner_id=order.partner_id.id)['value'])
                if not inv_line.get('account_analytic_id', False):
                    inv_line['account_analytic_id'] = \
                        self._prepare_analytic_account(line)
                inv_line['price_unit'] = line.price_unit
                inv_line['discount'] = line.discount
                inv_line['name'] = inv_name
                inv_line['invoice_line_tax_id'] = [
                        (6, 0, inv_line['invoice_line_tax_id'])]
                inv_line_ref.create(inv_line)
            inv_id.button_reset_taxes()
            order.signal_workflow('invoice')
            inv_id.signal_workflow('validate')

        return super(PosOrder, self).action_invoice()


class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.multi
    def wkf_action_close(self):

        self.ensure_one()
        order_env = self.env['pos.order']
        invoice_env = self.env['account.invoice']
        not_invoiced_order_ids = order_env.search([
            ('session_id', '=', self.id),
            ('invoice_id', '=', False)
        ], order='date_order asc')
        not_invoiced_order_ids.write({'state': 'done'})
        res = super(PosSession, self).wkf_action_close()
        not_invoiced_order_ids.write({'state': 'paid'})
        # Generate simplified invoice
        if not not_invoiced_order_ids or \
                not self.config_id.journal_id.sii_simplified_invoice:
            return res
        if not self.config_id.generic_customer_id:
            raise exceptions.Warning(_(
                '%s POS config has no generic customer defined. Please define '
                'one and try again') % self.config_id.name)
        first_ticket = not_invoiced_order_ids[0].name
        last_ticket = not_invoiced_order_ids[-1].name
        partner = self.config_id.generic_customer_id
        journal = self.config_id.journal_id
        currency = journal.currency or journal.company_id.currency_id
        invoice_vals = {
            'origin': self.name,
            'partner_id': partner.id,
            'journal_id': journal.id,
            'is_invoice_resume': True,
            'sii_invoice_resume_start': first_ticket,
            'sii_invoice_resume_end': last_ticket
        }
        change_partner = invoice_env.onchange_partner_id(
            'out_invoice', partner.id)
        invoice_vals.update(change_partner.get('value', {}))
        change_journal = invoice_env.onchange_journal_id(journal.id)
        invoice_vals.update(change_journal.get('value', {}))
        taxes_lines = {}
        ammount_total = 0
        for order in not_invoiced_order_ids:
            for line in order.lines:
                line_total = currency.round(
                    line.price_unit *
                    (1 - (line.discount or 0.0) / 100.0) * line.qty)
                tax_ids_key = ','.join([str(t.id) for t in line.tax_ids]) or\
                    'none'
                taxes_lines.setdefault(tax_ids_key, {
                    'amount_total': 0.0,
                    'tax_ids': line.tax_ids.ids
                })
                taxes_lines[tax_ids_key]['amount_total'] += line_total
                ammount_total += line_total
        is_refund = ammount_total < 0
        invoice_lines = []
        for tax_ids_key, values in taxes_lines.iteritems():
            invoice_lines.append((0, 0, {
                'name': 'Factura simplificada TPV %s - %s' % (
                    first_ticket, last_ticket),
                'price_unit': abs(values['amount_total']),
                'invoice_line_tax_id': [(6, 0, values['tax_ids'])],
                'account_analytic_id': self.config_id.account_analytic_id.id,
                'quantity': 1,
                'account_id': self.config_id.journal_id.default_debit_account_id.id,
            }))
        invoice_vals.update({
            'invoice_line': invoice_lines,
            'type': 'out_refund' if is_refund else 'out_invoice',
            'sii_refund_type': 'I' if is_refund else None,
            'sii_description': 'Factura simplificada TPV {} - {}'.format(
                first_ticket, last_ticket),
        })
        invoice = invoice_env.with_context(
                type=invoice_vals['type']
            ).create(invoice_vals)
        invoice.signal_workflow('invoice_open')

        self._reconcile_simplified_invoice(not_invoiced_order_ids, invoice)
        not_invoiced_order_ids.write({'invoice_id': invoice.id})
        invoice.signal_workflow('validate')
        return res

    @api.multi
    def _reconcile_simplified_invoice(self, orders, invoice):
        acc_default = self.env['ir.property'].get(
            'property_account_receivable', 'res.partner')
        grouped_data = {}
        for order in orders:
            current_company = order.sale_journal.company_id
            order_account = (
                order.partner_id and
                order.partner_id.property_account_receivable and
                order.partner_id.property_account_receivable.id or
                acc_default and acc_default.id or
                current_company.account_receivable.id
            )
            generic_customer = self.config_id.generic_customer_id
            grouped_data.setdefault(order_account, [])

            for each in order.statement_ids:
                if not each.journal_entry_id:
                    continue
                if each.account_id.id != order_account:
                    continue
                # Its needed a generic customer to reconcile
                each.journal_entry_id.partner_id = generic_customer
                each.journal_entry_id.mapped("line_id").write(
                        {'partner_id': generic_customer.id})

                valid_lines = each.journal_entry_id.line_id.filtered(
                        lambda l: (l.account_id.id == order_account and
                                   l.state == 'valid'))
                for line in valid_lines:
                    if (line.account_id.id == order_account and
                            line.state == 'valid'):
                        grouped_data[order_account].append(line.id)

        for key, value in grouped_data.iteritems():
            for line in invoice.move_id.line_id:
                if (line.account_id.id == key and
                        line.state == 'valid'):
                    grouped_data[key].append(line.id)

        # reconcile invoice
        for order_account, statement_lines in grouped_data.iteritems():
            if not statement_lines:
                continue
            context = self._context.copy()
            context.update({'active_ids': statement_lines})
            self.env['account.move.line.reconcile'].with_context(
                context).trans_rec_reconcile_full()

        return True
