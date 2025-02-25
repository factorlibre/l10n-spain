# -*- coding: utf-8 -*-
# © 2017 FactorLibre - Hugo Santos <hugo.santos@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, exceptions, fields, models, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    generic_customer_id = fields.Many2one(
        'res.partner', 'Generic Customer',
        help="Set a generic customer for simplified invoice records"
        " to send to SII")


class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.multi
    def wkf_action_close(self):
        self.ensure_one()
        order_env = self.env['pos.order']
        invoice_env = self.env['account.invoice']
        res = super(PosSession, self).wkf_action_close()
        # Generate simplified invoice
        not_invoiced_order_ids = order_env.search([
            ('session_id', '=', self.id),
            ('invoice_id', '=', False)
        ], order='date_order asc')
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
        invoice_vals = {
            'partner_id': partner.id,
            'type': 'out_invoice',
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
        for order in not_invoiced_order_ids:
            for line in order.lines:
                line_total = (line.price_unit *
                              (1 - (line.discount or 0.0) / 100.0) * line.qty)
                tax_ids_key = ','.join([str(t.id) for t in line.tax_ids]) or\
                    'none'
                taxes_lines.setdefault(tax_ids_key, {
                    'amount_total': 0.0,
                    'tax_ids': line.tax_ids.ids
                })
                taxes_lines[tax_ids_key]['amount_total'] += line_total
        invoice_lines = []
        for tax_ids_key, values in taxes_lines.iteritems():
            invoice_lines.append((0, 0, {
                'name': 'Factura simplificada TPV %s - %s' % (
                    first_ticket, last_ticket),
                'price_unit': values['amount_total'],
                'invoice_line_tax_id': [(6, 0, values['tax_ids'])],
                'quantity': 1,
                'account_id': self.config_id.journal_id.default_debit_account_id.id,
            }))
        invoice_vals['invoice_line'] = invoice_lines
        invoice_vals['sii_description'] =\
            'Factura simplificada TPV %s - %s' % (first_ticket, last_ticket)
        invoice = invoice_env.with_context(type='out_invoice').create(
            invoice_vals)
        invoice.signal_workflow('invoice_open')
        return res
