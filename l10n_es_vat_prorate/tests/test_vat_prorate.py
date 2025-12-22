# Copyright 2022 Creu Blanca
# Copyright 2023 Tecnativa - Pedro M. Baeza
# Copyright 2023 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.tests import common


@common.at_install(False)
@common.post_install(True)
class TestVatProrate(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        cls.company = cls.env.user.company_id
        cls.company.write(
            {
                "with_vat_prorate": True,
                "vat_prorate_ids": [
                    (0, 0, {"date": date(2000, 1, 1), "vat_prorate": 10}),
                    (0, 0, {"date": date(2001, 1, 1), "vat_prorate": 20}),
                ],
            }
        )
        cls.tax_sale_a = cls.env["account.tax"].create(
            {
                "name": "Tax Sale Company",
                "type_tax_use": "sale",
                "amount": "21.00",
                "price_include": False,
                "company_id": cls.company.id,
            }
        )
        cls.tax_purchase_a = cls.env["account.tax"].create(
            {
                "name": "Tax Purchase Company",
                "type_tax_use": "purchase",
                "with_vat_prorate": True,
                "amount": "21.00",
                "price_include": False,
                "company_id": cls.company.id,
            }
        )
        cls.product = cls.env['product.product'].create({
            "name": "Product Test",
            "list_price": 100.00,
            "supplier_taxes_id": [(6, 0, cls.tax_purchase_a.ids)],
            "taxes_id": [(6, 0, cls.tax_sale_a.ids)],
        })
        cls.journal_c1 = cls.env["account.journal"].create(
            {
                "name": "J1",
                "code": "J1",
                "type": "bank",
                "company_id": cls.company.id,
                "bank_acc_number": "123456",
            }
        )
        cls.partner = (
            cls.env["res.partner"]
            .with_context(force_company=cls.company.id)
            .create(
                {
                    "name": "Test supplier",
                }
            )
        )
        cls.account_type = cls.env.ref("account.data_account_type_payable")
        cls.account = cls.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST1",
                "user_type_id": cls.account_type.id,
                "reconcile": True,
            }
        )
        cls.account2 = cls.env["account.account"].create(
            {
                "name": "Test account 2",
                "code": "TEST2",
                "user_type_id": cls.account_type.id,
                "reconcile": True,
            }
        )

    def _create_invoice(self, multiline=False):
        invoice = self.env["account.invoice"].create(
            {
                "partner_id": self.partner.id,
                "journal_id": self.journal_c1.id,
                "account_id": self.account_type.id,
                "type": "in_invoice",
                "company_id": self.company.id,
            }
        )
        self.env["account.invoice.line"].create(
            {
                "product_id": self.product.id,
                "quantity": 1.0,
                "price_unit": 100.0,
                "invoice_id": invoice.id,
                "name": "product that cost 100",
                "account_id": self.account.id,
                "invoice_line_tax_ids": [(6, 0, [self.tax_purchase_a.id])],
            }
        )
        if multiline:
            self.env["account.invoice.line"].create(
                {
                    "product_id": self.product.id,
                    "quantity": 1.0,
                    "price_unit": 100.0,
                    "invoice_id": invoice.id,
                    "name": "product that cost 100",
                    "account_id": self.account2.id,
                    "invoice_line_tax_ids": [(6, 0, [self.tax_purchase_a.id])],
                }
            )
        return invoice

    def test_no_prorate_in_invoice(self):
        self.company.write(
            {"with_vat_prorate": False}
        )  # We want to be sure that it is executed properly
        invoice = self._create_invoice(False)
        # Calculate tax lines
        invoice._onchange_invoice_line_ids()
        self.assertEqual(1, len(invoice.invoice_line_ids))
        self.assertEqual(1, len(invoice.tax_line_ids))
        # Force prorate on created tax
        self.tax_purchase_a.with_vat_prorate = True
        invoice.action_invoice_open()
        self.assertEqual(3, len(invoice.move_id.line_ids))
        self.assertEqual(
            1, len(invoice.move_id.line_ids.filtered(lambda r: r.tax_line_id))
        )

    def test_prorate_in_invoice(self):
        invoice = self._create_invoice(False)
        # Calculate tax lines
        invoice._onchange_invoice_line_ids()
        self.assertEqual(1, len(invoice.invoice_line_ids))
        self.assertEqual(1, len(invoice.tax_line_ids))
        # Force prorate on created tax
        self.tax_purchase_a.with_vat_prorate = True
        invoice.action_invoice_open()
        self.assertEqual(4, len(invoice.move_id.line_ids))
        self.assertEqual(
            2, len(invoice.move_id.line_ids.filtered(lambda r: r.tax_line_id))
        )
