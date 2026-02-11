# Copyright 2026 Factor Libre
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.l10n_es_vat_book.tests import test_l10n_es_aeat_vat_book


class TestL10nEsVatBookOss(test_l10n_es_aeat_vat_book.TestL10nEsAeatVatBookBase):
    taxes_sale = {
        "S_IVA21S": (1500, 315),
    }

    def test_oss_tax_lines_force_zero_tax_and_deductible_amount(self):
        tax = self.env["account.tax"].search(
            [
                ("company_id", "=", self.company.id),
                ("description", "=", "S_IVA21S"),
            ],
            limit=1,
        )
        self.assertTrue(tax)
        tax.write({"oss_country_id": self.env.ref("base.fr").id})

        invoice = self._invoice_sale_create("2025-01-10")
        move_tax_lines = invoice.move_id.line_ids.filtered(
            lambda line: line.tax_line_id == tax
        )
        self.assertTrue(move_tax_lines)
        self.assertAlmostEqual(
            sum(line.credit - line.debit for line in move_tax_lines), 315.0
        )

        self.company.vat = "ES12345678Z"

        vat_book = self.env["l10n.es.vat.book"].create(
            {
                "name": "Test VAT Book OSS",
                "company_id": self.company.id,
                "company_vat": "1234567890",
                "contact_name": "Test owner",
                "type": "N",
                "support_type": "T",
                "contact_phone": "911234455",
                "year": 2025,
                "period_type": "1T",
                "date_start": "2025-01-01",
                "date_end": "2025-03-31",
            }
        )
        vat_book.button_calculate()

        tax_line = vat_book.issued_line_ids.tax_line_ids.filtered(
            lambda line: line.tax_id == tax
        )
        self.assertEqual(len(tax_line), 1)
        self.assertAlmostEqual(tax_line.base_amount, 1500.0)
        self.assertAlmostEqual(tax_line.tax_amount, 0.0)
        self.assertAlmostEqual(tax_line.deductible_amount, 0.0)
        self.assertAlmostEqual(tax_line.total_amount, 1500.0)
