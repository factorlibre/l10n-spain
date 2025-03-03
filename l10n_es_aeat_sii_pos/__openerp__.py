# -*- coding: utf-8 -*-
# © 2017 FactorLibre - Hugo Santos <hugo.santos@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Envio de factura simplificada resumen TPV a SII',
    'version': '8.0.1.2.5',
    'depends': [
        'point_of_sale',
        'l10n_es_aeat_sii',
        'l10n_es_aeat_sii_simplified_invoices',
        'pos_analytic_by_config',
    ],
    'category': "Accounting & Finance",
    'author': 'FactorLibre',
    'license': 'AGPL-3',
    'website': 'http://www.factorlibre.com',
    'data': [
        'views/account_journal_view.xml',
        'views/pos_view.xml',
        'reports/receipt_report.xml',
    ],
    'installable': True,
    'application': False
}
