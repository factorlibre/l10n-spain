# -*- coding: utf-8 -*-
# Copyright 2017 Santa Fixie SL - Juanjo Algaz <jalgaz@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    max_amount_total_simplified_invoice = fields.Float(
        string='Maximum allowable amount (simplified invoice)',
        help='Maximum allowable amount for simplified invoices in this company (taxes included).'
    )
