# © 2025 FactorLibre - Aritz Olea <aritz.olea@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools import float_round


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    prorate_id = fields.Many2one(
        string="Prorate",
        comodel_name="res.company.vat.prorate",
        compute="_compute_prorate_id",
        ondelete="restrict",
        store=True,
        copy=False,
    )
    with_special_vat_prorate = fields.Boolean(
        compute="_compute_prorate_id",
        store=True,
        copy=False,
    )
    with_vat_prorate = fields.Boolean(
        string="With VAT Prorate",
        help="The line will create a vat prorate",
        compute="_compute_with_vat_prorate",
        store=True,
        readonly=False,
        copy=False,
    )

    @api.depends("prorate_id", "company_id")
    def _compute_with_vat_prorate(self):
        for rec in self:
            rec.with_vat_prorate = rec.company_id.with_vat_prorate and (
                rec.prorate_id.type == "general"
                or rec.prorate_id.special_vat_prorate_default
            )

    @api.depends("company_id", "date", "date_invoice")
    def _compute_prorate_id(self):
        for rec in self:
            if rec.company_id.with_vat_prorate:
                prorate_date = rec.date or rec.date_invoice or fields.Date.today()
                rec.prorate_id = rec.company_id.get_prorate(prorate_date)
                rec.with_special_vat_prorate = rec.prorate_id.type == "special"
            else:
                rec.prorate_id = rec.with_special_vat_prorate = False

    @api.multi
    def get_lines_by_account(self, tax_id):
        self.ensure_one()
        lines_by_account = {}
        for line in self.invoice_line_ids.filtered(
            lambda line: tax_id in line.invoice_line_tax_ids.ids
        ):
            account_id = line.account_id.id
            lines_by_account.setdefault(account_id, [])
            lines_by_account[account_id].append(line)
        return lines_by_account

    @api.model
    def get_tax_parent(self, tax):
        if (
            tax.description and (
                tax.description.endswith("_1") or tax.description.endswith("_2")
            )
        ):
            parent_tax = self.env["account.tax"].search(
                [
                    ("company_id", "=", tax.company_id.id),
                    ("description", "=", tax.description[:-2])
                ], limit=1
            )
            return parent_tax if parent_tax else tax
        return tax

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        vals = super().finalize_invoice_move_lines(move_lines)
        new_move_lines = []
        for line in vals:
            line_values = line[2]
            if line_values.get("tax_line_id"):
                invoice_id = line_values.get("invoice_id")
                invoice = self.env["account.invoice"].browse(invoice_id)
                tax_id = line_values.get("tax_line_id")
                tax = self.env["account.tax"].browse(tax_id)
                if (
                    self.with_vat_prorate and tax.with_vat_prorate
                    and
                    (
                        not tax.prorate_account_ids or
                        line_values.get("account_id") in tax.prorate_account_ids.ids
                    )
                ):
                    currency_id = line_values.get("currency_id")
                    currency = (
                        self.env["res.currency"].browse(currency_id)
                        if currency_id else invoice.currency_id
                    )
                    prec = currency.rounding
                    prorate = invoice.prorate_id.vat_prorate
                    parent_tax_id = self.get_tax_parent(tax).id
                    lines_by_account = self.get_lines_by_account(parent_tax_id)
                    total_debit_prorat = float_round(
                        line_values["debit"] * (prorate / 100),
                        precision_rounding=prec,
                    )
                    total_credit_prorat = float_round(
                        line_values["credit"] * (prorate / 100),
                        precision_rounding=prec,
                    )
                    remaining_debit = line_values["debit"] - total_debit_prorat
                    remaining_credit = line_values["credit"] - total_credit_prorat
                    for line_account in lines_by_account.keys():
                        account_lines = lines_by_account[line_account]
                        amount = 0
                        for line in account_lines:
                            price_unit = (
                                line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                            )
                            taxes = tax.compute_all(
                                price_unit,
                                self.currency_id,
                                line.quantity,
                                line.product_id,
                                self.partner_id,
                            )["taxes"]
                            if taxes:
                                taxes = taxes[0]
                            amount += taxes.get("amount", 0)
                        new_line_vals = line_values.copy()

                        proportion = (
                            amount / line_values["debit"]
                            if line_values["debit"] else 0
                        )
                        new_line_vals["debit"] = float_round(
                            remaining_debit * proportion,
                            precision_rounding=prec,
                        )

                        proportion = (
                            amount / line_values["credit"]
                            if line_values["credit"] else 0
                        )
                        new_line_vals["credit"] = float_round(
                            remaining_credit * proportion,
                            precision_rounding=prec,
                        )

                        new_line_vals.update(
                            {
                                "vat_prorate": True,
                                "account_id": line_account,
                            }
                        )
                        new_move_lines.append((0, 0, new_line_vals))
                    line_values["debit"] = total_debit_prorat
                    line_values["credit"] = total_credit_prorat
        return vals + new_move_lines

    @api.model
    def _get_sii_tax_dict(self, tax_line, sign):
        tax_dict = super()._get_sii_tax_dict(tax_line, sign)
        move_lines = self.move_id.line_ids
        tax = tax_line.tax_id
        deductible = 0
        deductible_lines = move_lines.filtered(
            lambda line: line.tax_line_id == tax and not line.vat_prorate
        )
        for decuctible_line in deductible_lines:
            deductible += decuctible_line.balance * sign
        if deductible:
            tax_dict["CuotaDeducible"] = deductible
        return tax_dict
