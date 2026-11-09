# Copyright 2017-2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl

{
    'name': 'AEAT modelo 390',
    'version': '11.0.6.1.0',
    'category': "Localisation/Accounting",
    'author': "Tecnativa, Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/l10n-spain",
    'license': 'AGPL-3',
    'depends': ['l10n_es_aeat_mod303'],
    'data': [
        # 2017
        'data/aeat_export_mod390_sub01_data.xml',
        'data/aeat_export_mod390_sub02_data.xml',
        'data/aeat_export_mod390_sub03_data.xml',
        'data/aeat_export_mod390_sub04_data.xml',
        'data/aeat_export_mod390_sub05_data.xml',
        'data/aeat_export_mod390_sub06_data.xml',
        'data/aeat_export_mod390_sub07_data.xml',
        'data/aeat_export_mod390_sub08_data.xml',
        'data/aeat_export_mod390_main_data.xml',
        # 2018
        'data/aeat_export_mod390_2018_sub01_data.xml',
        'data/aeat_export_mod390_2018_sub02_data.xml',
        'data/aeat_export_mod390_2018_sub03_data.xml',
        'data/aeat_export_mod390_2018_sub04_data.xml',
        'data/aeat_export_mod390_2018_sub05_data.xml',
        'data/aeat_export_mod390_2018_sub06_data.xml',
        'data/aeat_export_mod390_2018_sub07_data.xml',
        'data/aeat_export_mod390_2018_sub08_data.xml',
        'data/aeat_export_mod390_2018_main_data.xml',
        # 2019
        'data/aeat_export_mod390_2019_sub01_data.xml',
        'data/aeat_export_mod390_2019_sub02_data.xml',
        'data/aeat_export_mod390_2019_sub03_data.xml',
        'data/aeat_export_mod390_2019_sub04_data.xml',
        'data/aeat_export_mod390_2019_sub05_data.xml',
        'data/aeat_export_mod390_2019_sub06_data.xml',
        'data/aeat_export_mod390_2019_sub07_data.xml',
        'data/aeat_export_mod390_2019_sub08_data.xml',
        'data/aeat_export_mod390_2019_main_data.xml',
        # 2021
        'data/aeat_export_mod390_2021_sub01_data.xml',
        'data/aeat_export_mod390_2021_sub02_data.xml',
        'data/aeat_export_mod390_2021_sub03_data.xml',
        'data/aeat_export_mod390_2021_sub04_data.xml',
        'data/aeat_export_mod390_2021_sub05_data.xml',
        'data/aeat_export_mod390_2021_sub06_data.xml',
        'data/aeat_export_mod390_2021_sub07_data.xml',
        'data/aeat_export_mod390_2021_sub08_data.xml',
        'data/aeat_export_mod390_2021_main_data.xml',
        # 2022
        "data/2022/aeat.model.export.config.csv",
        "data/2022/aeat.model.export.config.line.csv",
        # 2023
        "data/2023/aeat.model.export.config.csv",
        "data/2023/aeat.model.export.config.line.csv",
        # 2024
        "data/2024/aeat.model.export.config.csv",
        "data/2024/aeat.model.export.config.line.csv",
        # 2025
        "data/2025/aeat.model.export.config.csv",
        "data/2025/aeat.model.export.config.line.csv",
        # rest of stuff
        "views/mod390_view.xml",
        "views/account_invoice_view.xml",
        "views/account_move_view.xml",
        "security/ir.model.access.csv",
        "security/l10n_es_aeat_mod390_security.xml",
        'data/tax_code_map_mod390_data.xml',
        # 2024 tax mapping (after the previous map is closed)
        "data/2024/l10n.es.aeat.map.tax.csv",
        "data/2024/l10n.es.aeat.map.tax.line.csv",
    ],
    'installable': True,
    'maintainers': [
        'pedrobaeza',
    ],
}
