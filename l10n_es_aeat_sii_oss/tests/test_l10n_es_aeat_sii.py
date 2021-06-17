# Copyright 2021 FactorLibre - Rodrigo Bonilla <rodrigo.bonilla@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.l10n_es_aeat_sii.tests.test_l10n_es_aeat_sii import \
    TestL10nEsAeatSiiBase


class TestL10nEsAeatSiiBaseOss(TestL10nEsAeatSiiBase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestL10nEsAeatSiiBaseOss, cls).setUpClass()
        oss_wizard = cls.env["l10n.eu.oss.wizard"]
        xml_id = '%s_account_tax_template_s_iva21_bc' % cls.company.id
        cls.tax_21 = cls._get_or_create_tax(
            xml_id, "Test tax 21%", "sale", 21, cls.account_tax)
        # Elegimos FR y le apadimos un rate fijo para las pruebas.
        cls.oss_tax_rate_fr = cls.env.ref("l10n_eu_oss.oss_eu_rate_fr")
        cls.oss_tax_rate_fr.write({
            'general_rate': 20,
            'reduced_rate': 15,
            'superreduced_rate': 10,
            'second_superreduced_rate': 5,
        })
        # Lanzamos el wizard de l10n_eu_oss para crear las posiciones fiscales OSS.
        vals = oss_wizard.default_get(list(oss_wizard.fields_get()))
        vals.update({
            "company_id": cls.company.id,
            "general_tax": cls.tax_21.id,
        })
        oss_wizard_id = oss_wizard.create(vals)
        oss_wizard_id.generate_eu_oss_taxes()
        # Buscamos la posicion fiscal para FR creada para añadirle datos del SII
        cls.fpos_fr_id = cls.env["account.fiscal.position"].search([
            ("country_id", "=", cls.env.ref("base.fr").id),
            ])
        cls.fpos_fr_id.write({
            'sii_registration_key_sale': cls.env.ref(
                "l10n_es_aeat_sii_oss.aeat_sii_oss_mapping_registration_keys_1").id,
            'sii_exempt_cause': 'none',
            'sii_partner_identification_type': '2',
        })

    def test_invoice_sii_oss(self):
        tax_fr = self.fpos_fr_id.tax_ids.filtered(
            lambda x: x.tax_src_id.id == self.tax_21.id).mapped('tax_dest_id')
        self.partner.sii_simplified_invoice = True
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'date_invoice': '2018-02-01',
            'date': '2018-02-01',
            'type': 'out_invoice',
            'fiscal_position_id': self.fpos_fr_id.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.product.id,
                    'account_id': self.account_expense.id,
                    'account_analytic_id': self.analytic_account.id,
                    'name': 'Test line with iva FR',
                    'price_unit': 100,
                    'quantity': 1,
                    'invoice_line_tax_ids': [(6, 0, tax_fr.ids)],
                })],
            'sii_manual_description': '/',
        })
        invoices = invoice._get_sii_invoice_dict()
        ImporteTotal = invoices[
            'FacturaExpedida']['ImporteTotal']
        ClaveRegimenEspecialOTrascendencia = invoices[
            'FacturaExpedida']['ClaveRegimenEspecialOTrascendencia']
        self.assertEqual(100, ImporteTotal)
        self.assertEqual("17", ClaveRegimenEspecialOTrascendencia)
