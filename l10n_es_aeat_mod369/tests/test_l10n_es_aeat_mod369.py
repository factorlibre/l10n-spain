# Copyright 2022 Tecnativa - Pedro M. Baeza
# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0
import logging
import re

from odoo.exceptions import UserError

from odoo.addons.l10n_es_aeat.tests.test_l10n_es_aeat_mod_base import (
    TestL10nEsAeatModBase,
)

_logger = logging.getLogger("aeat.369")


class TestL10nEsAeatMod369Base(TestL10nEsAeatModBase):
    # Set 'debug' attribute to True to easy debug this test
    # Do not forget to include '--log-handler aeat:DEBUG' in Odoo command line
    debug = False

    def _get_oss_fiscal_position(self, country):
        """The 11.0 OSS wizard flags its fiscal positions as B2C."""
        return self.env["account.fiscal.position"].search(
            [
                ("country_id", "=", country.id),
                ("fiscal_position_type", "=", "b2c"),
                ("company_id", "=", self.company.id),
            ],
            limit=1,
        )

    def _oss_line(self, tax, price_unit=100, name="Test for OSS tax"):
        return (
            0,
            0,
            {
                "name": name,
                "account_id": self.accounts["700000"].id,
                "price_unit": price_unit,
                "quantity": 1,
                "invoice_line_tax_ids": [(6, 0, tax.ids)],
            },
        )

    def setUp(self):
        super(TestL10nEsAeatMod369Base, self).setUp()
        self.company.country_id = self.env.ref("base.es").id
        general_tax = self.env.ref(
            "l10n_es.%s_account_tax_template_s_iva21b" % self.company.id
        )
        reduced_tax = self.env.ref(
            "l10n_es.%s_account_tax_template_s_iva10b" % self.company.id
        )
        superreduced_tax = self.env.ref(
            "l10n_es.%s_account_tax_template_s_iva4b" % self.company.id
        )
        self.oss_taxes = {}
        self.oss_countries = {}
        self.sale_invoices = {}
        self.invoice_date = "2017-01-01"
        for country_key in ["FR", "DE"]:
            country = self.env.ref("base.%s" % country_key.lower())
            wizard = self.env["l10n.eu.oss.wizard"].create(
                {
                    "company_id": self.company.id,
                    "general_tax": general_tax.id,
                    "reduced_tax": reduced_tax.id,
                    "superreduced_tax": superreduced_tax.id,
                    "todo_country_ids": [(4, country.id)],
                }
            )
            wizard.generate_eu_oss_taxes()
            taxes = self.env["account.tax"].search(
                [
                    ("oss_country_id", "=", country.id),
                    ("company_id", "=", self.company.id),
                ]
            )
            fpo = self._get_oss_fiscal_position(country)
            tax_g = taxes[0]
            tax_r = taxes[1]
            tax_g.service_type = "goods"
            lines_data = [self._oss_line(tax_g)]
            if country_key == "FR":
                lines_data.append(self._oss_line(tax_r, price_unit=50))
            extra_vals = {
                "fiscal_position_id": fpo.id,
                "invoice_line_ids": lines_data,
            }
            invoice = self._invoice_sale_create(self.invoice_date, extra_vals)
            self.sale_invoices[country_key] = invoice
            self.oss_taxes[country_key] = taxes
            self.oss_countries[country_key] = country
        # 369
        model369_model = self.env["l10n.es.aeat.mod369.report"].sudo(
            self.account_manager
        )
        self.model369 = model369_model.create(
            {
                "company_id": self.company.id,
                "company_vat": "1234567890",
                "contact_name": "Test owner",
                # Statement type: N normal, C complementary, S substitutive.
                "type": "N",
                "support_type": "T",
                "contact_phone": "911234455",
                "year": 2017,
                "period_type": "1T",
                "date_start": "2017-01-01",
                "date_end": "2017-03-31",
            }
        )

    def _create_account_move(self):
        self.model369.journal_id = self.journal_misc.id
        self.model369.counterpart_account_id = self.accounts["477000"].id
        self.model369.button_confirm()
        self.model369.button_post()

    def test_01_amounts_by_country(self):
        """Bases and quotas are grouped per OSS country."""
        self.model369.button_calculate()
        total_sale_invoices_tax = 0
        for country_code in self.sale_invoices.keys():
            sale_invoice_by_key = self.sale_invoices[country_code]
            spain_goods_line_filter = self.model369.spain_goods_line_ids.filtered(
                lambda x: x.country_code == country_code and not x.is_page_8_line
            )
            spain_goods_line_amount = sum(
                line.amount for line in spain_goods_line_filter
            )
            self.assertEqual(spain_goods_line_amount, sale_invoice_by_key.amount_tax)
            spain_goods_line_base = sum(line.base for line in spain_goods_line_filter)
            self.assertEqual(
                spain_goods_line_base, sale_invoice_by_key.amount_untaxed
            )
            total_sale_invoices_tax += sale_invoice_by_key.amount_tax
        self.assertEqual(self.model369.total_amount, total_sale_invoices_tax)

    def test_02_refund_via_official_refund(self):
        """A credit note created through `account.invoice.refund()` carries
        `refund_invoice_id`, so it is recognised as a correction of a
        previous period."""
        origin = self.sale_invoices["FR"]
        refund = self._invoice_refund(origin, "2017-02-15")
        self.assertEqual(refund.refund_invoice_id, origin)
        refund_lines = refund.move_id.line_ids.filtered(
            lambda ml: ml.invoice_id.type == "out_refund"
            and ml.invoice_id.refund_invoice_id
        )
        self.assertTrue(refund_lines)

    def test_03_refund_without_origin_is_not_linked(self):
        """Characterisation test for the historical-data risk: a credit note
        NOT created through the official refund flow leaves
        `refund_invoice_id` empty, so the 369 cannot classify it as a
        correction of a previous period.

        In 11.0 only `account.invoice._prepare_refund()` populates that field.
        """
        fpo = self._get_oss_fiscal_position(self.oss_countries["FR"])
        manual_refund = (
            self.env["account.invoice"]
            .sudo(self.billing_user)
            .create(
                {
                    "company_id": self.company.id,
                    "partner_id": self.customer.id,
                    "date_invoice": "2017-02-20",
                    "type": "out_refund",
                    "account_id": self.customer.property_account_receivable_id.id,
                    "journal_id": self.journal_sale.id,
                    "fiscal_position_id": fpo.id,
                    "invoice_line_ids": [
                        self._oss_line(
                            self.oss_taxes["FR"][0], name="Manual credit note"
                        )
                    ],
                }
            )
        )
        manual_refund.action_invoice_open()
        self.assertFalse(manual_refund.refund_invoice_id)

    def test_04_account_move_positive_amount(self):
        self.model369.button_calculate()
        self._create_account_move()
        self.assertEqual(self.model369.name, self.model369.move_id.ref)
        self.assertEqual(self.model369.move_id.journal_id, self.model369.journal_id)
        # Select by account instead of by position: the ordering of
        # line_ids is not guaranteed.
        debit_line = self.model369.move_id.line_ids.filtered(
            lambda l: l.account_id == self.model369.counterpart_account_id
        )
        self.assertTrue(debit_line)
        self.assertEqual(sum(debit_line.mapped("debit")), self.model369.total_amount)

    def test_05_account_move_negative_amount(self):
        self.model369.button_calculate()
        self.model369.total_amount *= -1
        self._create_account_move()
        self.assertEqual(self.model369.name, self.model369.move_id.ref)
        credit_line = self.model369.move_id.line_ids.filtered(
            lambda l: l.account_id == self.model369.counterpart_account_id
        )
        self.assertTrue(credit_line)
        self.assertEqual(
            sum(credit_line.mapped("credit")), abs(self.model369.total_amount)
        )

    def test_06_account_move_zero_amount(self):
        self.model369.button_calculate()
        self.model369.total_amount = 0
        with self.assertRaises(UserError):
            self._create_account_move()

    def test_07_duplicate_oss_taxes(self):
        """Duplicate OSS taxes must not break field_number alignment
        and move lines using the duplicate tax must be included."""
        fr_general_tax = self.oss_taxes["FR"][0]
        dup_tax = self.env["account.tax"].create(
            {
                "name": "OSS FR duplicate [DE]",
                "amount": fr_general_tax.amount,
                "amount_type": "percent",
                "type_tax_use": fr_general_tax.type_tax_use,
                "oss_country_id": self.oss_countries["FR"].id,
                "company_id": self.company.id,
                "service_type": "goods",
            }
        )
        fpo = self._get_oss_fiscal_position(self.oss_countries["FR"])
        dup_invoice = self._invoice_sale_create(
            "2017-02-01",
            {
                "fiscal_position_id": fpo.id,
                "invoice_line_ids": [
                    self._oss_line(
                        dup_tax, price_unit=200, name="Test duplicate OSS tax"
                    )
                ],
            },
        )
        self.model369.button_calculate()
        fr_lines = self.model369.spain_goods_line_ids.filtered(
            lambda x: x.country_code == "FR" and not x.is_page_8_line
        )
        de_lines = self.model369.spain_goods_line_ids.filtered(
            lambda x: x.country_code == "DE" and not x.is_page_8_line
        )
        self.assertTrue(fr_lines)
        self.assertTrue(de_lines)
        expected_fr_tax = self.sale_invoices["FR"].amount_tax + dup_invoice.amount_tax
        self.assertEqual(sum(fr_lines.mapped("amount")), expected_fr_tax)
        self.assertEqual(
            sum(de_lines.mapped("amount")),
            self.sale_invoices["DE"].amount_tax,
        )

    def test_08_historical_audit_query(self):
        """The audit domain used to review historical data detects credit
        notes carrying OSS taxes whose origin invoice is not linked."""
        self._invoice_refund(self.sale_invoices["DE"], "2017-02-10")
        self.test_03_refund_without_origin_is_not_linked()
        oss_taxes = self.env["account.tax"].search(
            [
                ("oss_country_id", "!=", False),
                ("company_id", "=", self.company.id),
            ]
        )
        unlinked = self.env["account.invoice"].search(
            [
                ("company_id", "=", self.company.id),
                ("type", "=", "out_refund"),
                ("refund_invoice_id", "=", False),
                ("state", "in", ["open", "paid"]),
                ("invoice_line_ids.invoice_line_tax_ids", "in", oss_taxes.ids),
            ]
        )
        self.assertTrue(unlinked)
        self.assertTrue(
            all(not inv.refund_invoice_id for inv in unlinked),
            "The audit domain must only return credit notes without origin",
        )

    def test_09_previous_period_refund_lands_on_page_7(self):
        """End-to-end: a credit note whose original invoice belongs to an
        earlier period is reported as a correction of a previous period.

        This exercises the whole chain the backport had to adapt: detecting
        the credit note through `invoice_id`, resolving its origin through
        `refund_invoice_id`, and deriving the fiscal year and period from a
        date that is read as a string.
        """
        # Original invoice BEFORE the reported quarter (1T 2017).
        fpo = self._get_oss_fiscal_position(self.oss_countries["FR"])
        origin = self._invoice_sale_create(
            "2016-11-15",
            {
                "fiscal_position_id": fpo.id,
                "invoice_line_ids": [self._oss_line(self.oss_taxes["FR"][0])],
            },
        )
        # Credit note INSIDE the reported quarter.
        refund = self._invoice_refund(origin, "2017-02-10")
        self.assertEqual(refund.refund_invoice_id, origin)

        self.model369.button_calculate()

        refund_groups = self.model369.refund_line_ids
        self.assertTrue(
            refund_groups, "The credit note must produce a page 7 group"
        )
        self.assertTrue(all(g.is_refund for g in refund_groups))
        # Year and period come from the ORIGINAL invoice, not from the note.
        self.assertEqual(refund_groups.mapped("refund_fiscal_year"), [2016])
        self.assertEqual(refund_groups.mapped("refund_period"), ["T4"])
        self.assertEqual(
            refund_groups.mapped("oss_country_id"), self.oss_countries["FR"]
        )
        # The correction is negative: it subtracts from the period.
        self.assertTrue(sum(refund_groups.mapped("tax_correction")) < 0)
        # And it is kept out of the ordinary goods lines of the quarter.
        self.assertNotIn(
            refund.move_id.line_ids,
            self.model369.spain_goods_line_ids.mapped(
                "mod369_line_ids.tax_line_id.move_line_ids"
            ),
        )

    def _boe_blocks(self, contents, strip=True):
        """Return the BOE blocks as {tag: payload}, padding optional."""
        return {
            match.group(1).decode(): (
                match.group(2).strip() if strip else match.group(2)
            )
            for match in re.finditer(
                br"<T(369\d\d)>(.*?)</T\1>", contents, re.DOTALL
            )
        }

    def _export_boe(self):
        wizard = self.env["l10n.es.aeat.report.export_to_boe"].create({})
        return wizard.action_get_file_from_config(self.model369)

    def test_10_export_file_equivalence(self):
        """Every figure of the BOE file, and the width of every block, is
        pinned.

        The expected bytes were captured by running this same fixture
        against the implementation this branch replaces, and checked to
        still hold afterwards. That check is not reproducible from the
        tree, so read these literals as a recorded baseline, not as proof
        on their own.
        """
        self.model369.button_calculate()
        contents = self._export_boe()
        self.assertEqual(
            self._boe_blocks(contents),
            {
                "36900": b"",
                # Declared quota: 44.00 = 20.00 + 5.00 + 19.00.
                "36904": b"MOSS DI                      00000000000004400 "
                b"ES123456789      SPANISH TEST COMPANY"
                + b" " * 105
                + b"2017T01                0",
                # Base and quota per country and rate: FR 20%, FR 10%, DE 19%.
                "36905": b"FR02000 0000000000001000000000000000002000"
                b"FR01000 0000000000000500000000000000000500"
                b"DE01900 0000000000001000000000000000001900",
                "36906": b"",
                "36907": b"",
                "36908": b"",
                "36909": b"",
            },
        )
        # Each field is padded to its declared `size` (`_format_string`),
        # so a width change in a field that comes out blank leaves the
        # payloads above untouched. Five of these blocks are blank here.
        self.assertEqual(
            {
                tag: len(payload)
                for tag, payload in self._boe_blocks(
                    contents, strip=False
                ).items()
            },
            {
                "36900": 93,
                "36904": 1406,
                "36905": 1194,
                "36906": 1670,
                "36907": 1670,
                "36908": 746,
                "36909": 5786,
            },
        )

    def test_11_totals_are_frozen_snapshot(self):
        """The totals keep what `calculate()` put in them.

        They no longer follow their source lines on every read, which is
        what made the form walk the whole period again each time it was
        opened. Refreshing them is now an explicit recalculation.
        """
        self.model369.button_calculate()
        page_8 = self.model369.total_line_ids[0]
        base, amount = page_8.base, page_8.amount
        self.assertTrue(amount, "the fixture must produce a quota to freeze")

        # Detach the lines the totals were built from: a recomputation on
        # read would drop them to zero.
        page_8.write({"mod369_line_ids": [(5, 0, 0)]})
        page_8.invalidate_cache()

        self.assertEqual(page_8.base, base)
        self.assertEqual(page_8.amount, amount)

    def test_12_page_8_gathers_previous_period_corrections(self):
        """The page 8 total of a country carries the corrections of the
        page 7 groups of that same country.

        `calculate()` sums the corrections as it walks the tax lines, so
        this pins the figure the AEAT is told to refund.
        """
        fpo = self._get_oss_fiscal_position(self.oss_countries["FR"])
        origin = self._invoice_sale_create(
            "2016-11-15",
            {
                "fiscal_position_id": fpo.id,
                "invoice_line_ids": [self._oss_line(self.oss_taxes["FR"][0])],
            },
        )
        self._invoice_refund(origin, "2017-02-10")

        self.model369.button_calculate()

        france = self.oss_countries["FR"]
        page_8 = self.model369.total_line_ids.filtered(
            lambda group: group.oss_country_id == france
        )
        self.assertEqual(len(page_8), 1)
        corrections = sum(
            self.model369.refund_line_ids.filtered(
                lambda group: group.oss_country_id == france
            ).mapped("tax_correction")
        )
        self.assertTrue(corrections < 0, "The correction must subtract")
        self.assertEqual(page_8.neg_corrections, corrections)
        self.assertEqual(page_8.result_total, page_8.amount + corrections)
        # A country of another report keeps its own corrections.
        germany_page_8 = self.model369.total_line_ids.filtered(
            lambda group: group.oss_country_id == self.oss_countries["DE"]
        )
        self.assertEqual(len(germany_page_8), 1)
        self.assertEqual(germany_page_8.neg_corrections, 0)
        # Germany only sells goods here, so its quota lands on the goods page
        # and not on the services one.
        self.assertEqual(germany_page_8.page_4_total, germany_page_8.amount)
        self.assertEqual(germany_page_8.page_3_total, 0)
        self.assertEqual(
            germany_page_8.page_3_4_total, germany_page_8.page_4_total
        )
        # Supplies from Spain never feed the non-Spanish pages.
        self.assertEqual(germany_page_8.page_5_total, 0)
        self.assertEqual(germany_page_8.page_6_total, 0)
        self.assertEqual(germany_page_8.page_5_6_total, 0)
        # The quota of the period outweighs the correction, so the country
        # still has an amount to pay.
        self.assertTrue(page_8.result_total > 0)
        self.assertEqual(page_8.total_deposit, page_8.result_total)
        self.assertEqual(page_8.total_return, 0)

    def test_13_breakdown_leaves_out_previous_period_corrections(self):
        """The magnifying glass of a grouped line lists the journal items
        behind it, without the ones reported as corrections on page 7.

        Its criterion now reads what `calculate()` stored instead of
        working it out again, so it is worth pinning that both agree.
        """
        fpo = self._get_oss_fiscal_position(self.oss_countries["FR"])
        origin = self._invoice_sale_create(
            "2016-11-15",
            {
                "fiscal_position_id": fpo.id,
                "invoice_line_ids": [self._oss_line(self.oss_taxes["FR"][0])],
            },
        )
        self._invoice_refund(origin, "2017-02-10")

        self.model369.button_calculate()

        corrections = self.model369.refund_line_ids.mapped("refund_line_ids")
        self.assertTrue(corrections, "the fixture must produce a correction")
        france = self.oss_countries["FR"]
        page_8 = self.model369.total_line_ids.filtered(
            lambda group: group.oss_country_id == france
        )
        source = page_8.mapped("mod369_line_ids.tax_line_id.move_line_ids")
        self.assertTrue(
            set(corrections.ids) & set(source.ids),
            "the corrections must be among the lines the group is built from",
        )
        listed = page_8.get_calculated_move_lines()["domain"][0][2]
        self.assertTrue(listed)
        self.assertFalse(set(corrections.ids) & set(listed))

    def test_14_origin_without_date_is_not_a_previous_period_correction(self):
        """A credit note whose original invoice carries no date stays in the
        period as a supply.

        Nothing places that invoice in an earlier period, and page 7 derives
        the year and the period from that same date, so it could not be
        reported there either.
        """
        fpo = self._get_oss_fiscal_position(self.oss_countries["FR"])
        origin = self._invoice_sale_create(
            "2016-11-15",
            {
                "fiscal_position_id": fpo.id,
                "invoice_line_ids": [self._oss_line(self.oss_taxes["FR"][0])],
            },
        )
        refund = self._invoice_refund(origin, "2017-02-10")
        origin.write({"date_invoice": False})
        self.assertEqual(refund.refund_invoice_id, origin)

        self.model369.button_calculate()

        self.assertFalse(
            self.model369.refund_line_ids,
            "an undated origin must not produce a page 7 correction",
        )
