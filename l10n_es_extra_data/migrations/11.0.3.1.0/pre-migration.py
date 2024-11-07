import odoo
import logging


_logger = logging.getLogger(__name__)


def fix_manually_created_taxes(env):
    extra_taxes_names = [
        "IVA 0% Adquisición Intracomunitario. Bienes corrientes",
        "IVA 10% ISP (bienes de inversión)",
        "IVA 10% ISP (bienes de inversión) (1)",
        "IVA 10% ISP (bienes de inversión) (2)",
        "IVA 21% ISP (bienes de inversión)",
        "IVA 21% ISP (bienes de inversión) (1)",
        "IVA 21% ISP (bienes de inversión) (2)",
        "2% IVA soportado (bienes corrientes)",
        "IVA 2% Importaciones bienes corrientes",
        "IVA 2% Adquisición Intracomunitario. Bienes corrientes",
        "IVA 2% Adquisición de bienes intracomunitarios (1)",
        "IVA 2% Adquisición de bienes intracomunitarios (2)",
        "IVA 2% Adquisición Intracomunitario. Servicios corrientes",
        "IVA 2% Adquisición de servicios intracomunitarios (1)",
        "IVA 2% Adquisición de servicios intracomunitarios (2)",
        "IVA 2% Adquisición de servicios extracomunitarios",
        "IVA 2% Adquisición de servicios extracomunitarios (1)",
        "IVA 2% Adquisición de servicios extracomunitarios (2)",
        "2% IVA Soportado no deducible",
        "2% IVA soportado (servicios corrientes)",
        "IVA 4% ISP (bienes de inversión)",
        "IVA 4% ISP (bienes de inversión) (1)",
        "IVA 4% ISP (bienes de inversión) (2)",
        "7.5% IVA soportado (bienes corrientes)",
        "IVA 7.5% Importaciones bienes corrientes",
        "IVA 7.5% Adquisición Intracomunitario. Bienes corrientes",
        "IVA 7.5% Adquisición de bienes intracomunitarios (1)",
        "IVA 7.5% Adquisición de bienes intracomunitarios (2)",
        "IVA 7.5% Adquisición de servicios intracomunitarios",
        "IVA 7.5% Adquisición de servicios intracomunitarios (1)",
        "IVA 7.5% Adquisición de servicios intracomunitarios (2)",
        "IVA 7.5% Adquisición de servicios extracomunitarios",
        "IVA 7.5% Adquisición de servicios extracomunitarios (1)",
        "IVA 7.5% Adquisición de servicios extracomunitarios (2)",
        "7.5% IVA Soportado no deducible",
        "7.5% IVA soportado (servicios corrientes)",
        "0.26% Recargo Equivalencia Compras",
        "1% Recargo Equivalencia Compras",
        "IVA 0% (Bienes)",
        "IVA 2% (Bienes)",
        "IVA 2% (Servicios)",
        "IVA 7.5% (Bienes)",
        "IVA 7.5% (Servicios)",
        "0.26% Recargo Equivalencia Ventas",
        "1% Recargo Equivalencia Ventas",
    ]
    # Search all manually created tax templates
    manually_created_taxes = env["account.tax.template"]
    extra_taxes = env["account.tax.template"].search(
        [("name", "in", extra_taxes_names)]
    )
    extra_taxes_with_external_identifiers_ids = (
        env["ir.model.data"]
        .search(
            [
                ("model", "=", "account.tax.template"),
                ("res_id", "in", extra_taxes.ids),
            ]
        )
        .mapped("res_id")
    )
    extra_taxes_without_external_identifiers = extra_taxes.filtered(
        lambda x: x.id not in extra_taxes_with_external_identifiers_ids
    )
    manually_created_taxes |= extra_taxes_without_external_identifiers
    manually_created_taxes_data = env["ir.model.data"].search(
        [
            ("model", "=", "account.tax.template"),
            ("res_id", "in", extra_taxes.ids),
            ("module", "!=", "l10n_es_extra_data"),
        ]
    )
    manually_created_taxes |= env["account.tax.template"].browse(
        manually_created_taxes_data.mapped("res_id")
    )
    for tax in manually_created_taxes:
        tax.name = tax.name + "_old"
        _logger.info("Renamed manually created Tax Template to %s" % tax.name)


def fix_modified_external_identifiers(env):
    old_external_identifiers = {
        "account_tax_template_p_iva75_ic_sc_1": "account_tax_template_p_iva7-5_ic_sc_1",
        "account_tax_template_p_iva75_ic_sc_2": "account_tax_template_p_iva7-5_ic_sc_2",
        "account_tax_template_p_iva2_ic_bc1": "account_tax_template_p_iva2_ic_bc_1",
        "account_tax_template_p_iva2_ic_sc1": "account_tax_template_p_iva2_ic_sc_1",
    }
    external_identifiers = env["ir.model.data"].search(
        [
            ("model", "=", "account.tax.template"),
            ("name", "in", list(old_external_identifiers.keys())),
        ]
    )
    for ext_id in external_identifiers:
        ext_id.name = old_external_identifiers[ext_id.name]
        _logger.info("Renamed Old external identifier to %s" % ext_id.name)


def migrate(cr, version):
    if not version:
        return
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    fix_manually_created_taxes(env)
    fix_modified_external_identifiers(env)
