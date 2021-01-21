# © 2020 FactorLibre - Gerardo Gomez-Caminero <gerardo.gomez@factorlibre.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestAccountInvoice(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.AccountInvoice = self.env['account.invoice']
        self.ResCompany = self.env['res.company']
        self.ResPartner = self.env['res.partner']
        self.invoice = self.AccountInvoice.new({
            'date_invoice': '2021-10-01',
            'date': '2021-01-01',
            'company_id': self.ResCompany.new({
                'vat': 'ES123456789',
            }),
            'partner_id': self.ResPartner.new({
                'commercial_partner_id': self.ResPartner.new({
                    'name': 'NAMETEST_COMERCIALPARTNER',
                }),
            }),
        })

    def test_get_sii_invoice_dict_with_thirdparty_code_is_ok(self):
        invoice = self.invoice
        invoice.sii_force_number = 'TESTNUMBER'
        invoice.sii_thirdparty_invoice = True

        inv_dict = invoice._get_sii_invoice_dict_out()
        self.assertEqual(
            'S',
            inv_dict.get(
                "FacturaExpedida",
                {}).get("EmitidaPorTercerosODestinatario", False)
        )

    def test_get_sii_invoice_dict_normal_no_thirdparty_code(self):
        invoice = self.invoice
        invoice.sii_thirdparty_invoice = False

        inv_dict = invoice._get_sii_invoice_dict_out()
        self.assertEqual(
            'EsNormal',
            inv_dict.get(
                "FacturaExpedida",
                {}).get("EmitidaPorTercerosODestinatario", 'EsNormal')
        )
