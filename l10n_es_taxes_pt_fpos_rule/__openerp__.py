# -*- coding: utf-8 -*-
# © 2016 FactorLibre - Hugo Santos <hugo.santos@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Spanish account configuration: Portugal fiscal position rule',
    'version': '8.0.1.0.0',
    'depends': [
        'l10n_es_taxes_pt',
        'account_fiscal_position_rule'
    ],
    'author': 'Odoo Community Association (OCA),FactorLibre',
    'category': 'Localization/Account Charts',
    'license': 'AGPL-3',
    'website': 'http://www.factorlibre.com',
    'data': [
        'data/fpos_rule_pt.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': True
}
