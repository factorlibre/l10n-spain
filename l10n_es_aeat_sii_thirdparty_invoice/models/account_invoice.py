# -*- coding: utf-8 -*-
# © 2020 FactorLibre - Gerardo Gomez-Caminero <gerardo.gomez@factorlibre.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    internal_number = fields.Char(
        compute='_force_number',
        states={'draft': [('readonly', False)]}
    )
    sii_thirdparty_invoice = fields.Boolean(
        string="SII third-party invoice", copy=False
    )
    sii_force_number = fields.Char(
        string='SII force number', copy=False,
    )

    @api.depends('sii_force_number')
    def _force_number(self):
        for record in self:
            record.internal_number = record.sii_force_number

    @api.multi
    def _get_sii_invoice_dict_out(self, cancel=False):
        inv_dict = super(
                AccountInvoice,
                self
            )._get_sii_invoice_dict_out(cancel)
        if self.sii_thirdparty_invoice and self.sii_force_number:
            inv_dict['IDFactura'].update({
                'NumSerieFacturaEmisor': self.sii_force_number,
            })
        if not cancel:
            if self.sii_thirdparty_invoice:
                inv_dict['FacturaExpedida'].update({
                    'EmitidaPorTercerosODestinatario': 'S',
                })

        return inv_dict
