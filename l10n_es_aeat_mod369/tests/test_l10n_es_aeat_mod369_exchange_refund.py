# Copyright 2026 Factor Libre - Iván Bósquez
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

from . import test_l10n_es_aeat_mod369


class TestL10nEsAeatMod369ExchangeRefund(
    test_l10n_es_aeat_mod369.TestL10nEsAeatMod369Base
):
    def _fr_tax(self, rate):
        tax = self.oss_taxes["FR"].filtered(lambda tax: tax.amount == rate)
        self.assertEqual(len(tax), 1)
        return tax

    def _line_vals(self, tax, price_unit):
        return (
            0,
            0,
            {
                "name": "Test for OSS tax",
                "account_id": self.accounts["700000"].id,
                "price_unit": price_unit,
                "quantity": 1,
                "tax_ids": [(6, 0, tax.ids)],
            },
        )

    def _previous_period_refund(self, lines):
        origin = self._invoice_sale_create(
            "2016-11-15",
            {
                "fiscal_position_id": self.sale_invoices["FR"].fiscal_position_id.id,
                "invoice_line_ids": lines,
            },
        )
        refund = origin._reverse_moves(
            [{"date": "2017-02-10", "invoice_date": "2017-02-10"}]
        )
        refund.action_post()
        return refund

    def _fr_groups(self):
        self.model369.button_calculate()
        france = self.oss_countries["FR"]
        corrections = self.model369.refund_line_ids.filtered(
            lambda group: group.oss_country_id == france
        )
        page_8 = self.model369.total_line_ids.filtered(
            lambda group: group.oss_country_id == france
        )
        self.assertEqual(len(corrections), 1)
        self.assertEqual(len(page_8), 1)
        self.assertEqual(corrections.refund_fiscal_year, 2016)
        self.assertEqual(corrections.refund_period, "T4")
        return corrections, page_8

    def test_exchange_refund_corrects_with_net_of_both_quotas(self):
        refund = self._previous_period_refund(
            [
                self._line_vals(self._fr_tax(20), 43.10),
                self._line_vals(self._fr_tax(10), -10.10),
            ]
        )
        quota_lines = refund.line_ids.filtered("tax_line_id")
        self.assertAlmostEqual(sum(quota_lines.mapped("debit")), 8.62)
        self.assertAlmostEqual(sum(quota_lines.mapped("credit")), 1.01)
        corrections, page_8 = self._fr_groups()
        self.assertAlmostEqual(corrections.tax_correction, -7.61)
        self.assertEqual(corrections.tax_correction_str, "-0000000000000761")
        self.assertAlmostEqual(page_8.neg_corrections, -7.61)

    def test_exchange_refund_with_positive_net(self):
        self._previous_period_refund(
            [
                self._line_vals(self._fr_tax(5.5), 100.00),
                self._line_vals(self._fr_tax(20), -30.00),
            ]
        )
        corrections, page_8 = self._fr_groups()
        self.assertAlmostEqual(corrections.tax_correction, 0.50)
        self.assertEqual(corrections.tax_correction_str, "00000000000000050")
        self.assertAlmostEqual(page_8.neg_corrections, 0.50)

    def test_regular_refund_unchanged(self):
        self._previous_period_refund(
            [
                self._line_vals(self._fr_tax(20), 9.05),
                self._line_vals(self._fr_tax(10), 10.10),
            ]
        )
        corrections, page_8 = self._fr_groups()
        self.assertAlmostEqual(corrections.tax_correction, -2.82)
        self.assertEqual(corrections.tax_correction_str, "-0000000000000282")
        self.assertAlmostEqual(page_8.neg_corrections, -2.82)
