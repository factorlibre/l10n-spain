# © 2025 FactorLibre - Aritz Olea <aritz.olea@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    vat_prorate = fields.Boolean(
        string="Is vat prorate",
        help="The line is a vat prorate",
        copy=False,
    )
