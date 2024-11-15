# © 2024 FactorLibre - Sergio Bustamante <sergio.bustamante@factorlibre.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    cip = fields.Char(string="CIP", help="Plastic Identification Code", size=13)
