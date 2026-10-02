# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Spain - VERI*FACTU QR code on POS tickets",
    "summary": "Print the AEAT VERI*FACTU QR code at the top of POS tickets",
    "category": "Point Of Sale",
    "author": "FactorLibre, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-spain",
    "license": "AGPL-3",
    "version": "11.0.1.0.0",
    "depends": [
        "point_of_sale",
        "l10n_es_pos",
    ],
    "external_dependencies": {
        "python": ["qrcode"],
    },
    "data": [
        "views/assets.xml",
        "views/pos_config_views.xml",
    ],
    "qweb": [
        "static/src/xml/pos.xml",
    ],
    "installable": True,
}
