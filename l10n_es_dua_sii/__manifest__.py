# Copyright 2017 Consultoría Informática Studio 73 S.L.
# Copyright 2017 Comunitea Servicios Tecnológicos S.L.
# Copyright 2019 Tecnativa - Alexandre Díaz
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Suministro Inmediato de Información de importaciones con DUA",
    "version": "11.0.1.0.2",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/l10n-spain",
    "author": "Studio73, "
              "Comunitea, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_aeat_sii",
        "l10n_es_dua",
    ],
    "data": [
        "data/tax_code_map_dua_sii_data.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": True,
}
