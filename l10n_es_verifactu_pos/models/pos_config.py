# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

VERIFACTU_PRODUCTION_URL = (
    "https://www2.agenciatributaria.gob.es/wlpl/TIKE-CONT/ValidarQR")


class PosConfig(models.Model):
    _inherit = "pos.config"

    verifactu_enabled = fields.Boolean(
        string="VERI*FACTU",
        default=False,
        help="Print the AEAT VERI*FACTU QR code at the top of the tickets "
             "of this POS.",
    )
    verifactu_base_url = fields.Char(
        string="VERI*FACTU QR base URL",
        default=VERIFACTU_PRODUCTION_URL,
        help="AEAT verification service URL used to build the QR code. "
             "Use https://prewww2.aeat.es/wlpl/TIKE-CONT/ValidarQR for "
             "testing.",
    )
    verifactu_issuer_vat = fields.Char(
        string="VERI*FACTU issuer VAT",
        compute="_compute_verifactu_issuer_vat",
    )

    @api.multi
    def _get_verifactu_issuer_vat(self):
        """Issuer VAT (NIF) for the QR code, without country prefix.

        Extension point: override it to take the VAT from another source.
        """
        self.ensure_one()
        vat = self.company_id.partner_id.vat or ""
        vat = re.sub(r"[^A-Za-z0-9]", "", vat).upper()
        if len(vat) == 11 and vat.startswith("ES"):
            vat = vat[2:]
        return vat

    @api.multi
    @api.depends("company_id.partner_id.vat")
    def _compute_verifactu_issuer_vat(self):
        for config in self:
            config.verifactu_issuer_vat = config._get_verifactu_issuer_vat()

    @api.constrains("verifactu_enabled", "iface_l10n_es_simplified_invoice")
    def _check_verifactu_enabled(self):
        for config in self.filtered("verifactu_enabled"):
            if not config.iface_l10n_es_simplified_invoice:
                raise ValidationError(_(
                    "VERI*FACTU requires simplified invoices to be enabled "
                    "in the Point of Sale %s.") % config.name)
            if not config.verifactu_issuer_vat:
                raise ValidationError(_(
                    "VERI*FACTU requires a VAT number for the issuer of the "
                    "Point of Sale %s.") % config.name)
