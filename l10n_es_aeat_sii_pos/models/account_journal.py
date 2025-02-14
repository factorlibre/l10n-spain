# -*- coding: utf-8 -*-
# © 2017 FactorLibre - Hugo Santos <hugo.santos@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    sii_simplified_invoice = fields.Boolean(
        'Send simplified invoice SII',
        help="Send invoices from this journal as simplified"
        " invoices with F4 key")
