# © 2020 FactorLibre - Gerardo Gomez-Caminero <gerardo.gomez@factorlibre.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    sii_thirdparty_invoice = fields.Boolean(
        string="SII third-party invoice", copy=False
    )

    @api.multi
    def _get_sii_invoice_dict_out(self, cancel=False):
        inv_dict = super(AccountInvoice, self)._get_sii_invoice_dict_out(
            cancel
        )
        if not cancel:
            if self.sii_thirdparty_invoice:
                inv_dict["FacturaExpedida"].update(
                    {
                        "EmitidaPorTercerosODestinatario": "S",
                    }
                )

        return inv_dict
