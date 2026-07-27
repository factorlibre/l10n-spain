# Copyright 2017 Eficent Business & IT Consult. Services <contact@eficent.com>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging
from odoo import exceptions
from odoo.addons.l10n_es_aeat.tests.test_l10n_es_aeat_mod_base import \
    TestL10nEsAeatModBase

_logger = logging.getLogger('aeat.349')


class TestL10nEsAeatMod349Base(TestL10nEsAeatModBase):
    # Set 'debug' attribute to True to easy debug this test
    # Do not forget to include '--log-handler aeat:DEBUG' in Odoo command line
    debug = False
    taxes_sale = {
        # tax code: (base, tax_amount)
        'S_IVA0_IC': (2400, 0),
    }
    taxes_purchase = {
        # tax code: (base, tax_amount)
        'P_IVA21_IC_BC': (150, 0),
        'P_IVA21_IC_BC//2': (150, 0),
    }

    def test_model_349(self):
        # Add some test data
        self.customer.write({
            'vat': 'BE0411905847',
            'country_id': self.env.ref('base.be').id,
        })
        self.supplier.write({
            'vat': 'BG0000100159',
            'country_id': self.env.ref('base.bg').id,
        })
        # Data for 1T 2017
        # Purchase invoices
        p1 = self._invoice_purchase_create('2017-01-01')
        p2 = self._invoice_purchase_create('2017-01-02')
        self._invoice_purchase_create('2017-01-03')
        self._invoice_refund(p2, '2017-01-02')
        # Sale invoices
        s1 = self._invoice_sale_create('2017-01-01')
        s2 = self._invoice_sale_create('2017-01-02')
        s3 = self._invoice_sale_create('2017-01-03')
        self._invoice_refund(s2, '2017-01-02')
        # Create model
        model349_model = self.env['l10n.es.aeat.mod349.report'].sudo(
            self.account_manager)
        model349 = model349_model.create({
            'name': '3490000000001',
            'company_id': self.company.id,
            'company_vat': '1234567890',
            'contact_name': 'Test owner',
            'type': 'N',
            'support_type': 'T',
            'contact_phone': '911234455',
            'year': 2017,
            'period_type': '1T',
            'date_start': '2017-01-01',
            'date_end': '2017-03-31',
        })
        # Calculate
        _logger.debug('Calculate AEAT 349 1T 2017')
        model349.button_calculate()
        self.assertEqual(model349.total_partner_records, 2)
        # p1 + p2 - p2* + p3 + s1 + s2 - s2* + s3 =
        # 300 + 300 - 300 + 300 + 2400 + 2400 - 2400 + 2400
        self.assertEqual(model349.total_partner_records_amount, 5400.00)
        self.assertEqual(model349.total_partner_refunds, 0)
        self.assertEqual(model349.total_partner_refunds_amount, 0.0)
        a_record = model349.partner_record_ids.filtered(
            lambda x: x.operation_key == 'A')
        self.assertEqual(len(a_record), 1)
        self.assertEqual(len(a_record.record_detail_ids), 8)
        self.assertEqual(a_record.partner_vat,  self.supplier.vat)
        self.assertEqual(a_record.country_id, self.supplier.country_id)
        # p1 + p2 - p2* + p3 = 300 + 300 - 300 + 300
        self.assertEqual(a_record.total_operation_amount, 600)
        e_record = model349.partner_record_ids.filtered(
            lambda x: x.operation_key == 'E')
        self.assertEqual(len(e_record), 1)
        self.assertEqual(len(e_record.record_detail_ids), 4)
        self.assertEqual(e_record.partner_vat, self.customer.vat)
        self.assertEqual(e_record.country_id, self.customer.country_id)
        # s1 + s2 - s2* + s3 = 2400 + 2400 - 2400 + 2400
        self.assertEqual(e_record.total_operation_amount, 4800)
        # Now we delete detailed records to see if totals are recomputed
        model349.partner_record_detail_ids.filtered(
            lambda x: x.invoice_id == p1
        ).unlink()
        self.assertEqual(a_record.total_operation_amount, 300)
        model349.partner_record_detail_ids.filtered(
            lambda x: x.invoice_id == s1
        ).unlink()
        self.assertEqual(e_record.total_operation_amount, 2400)
        # Create a complementary presentation for 1T 2017. We expect the
        #  application to propose the records that were not included in the
        # first presentation.
        model349_c = model349_model.create({
            'name': '3490000000002',
            'company_id': self.company.id,
            'company_vat': '1234567890',
            'contact_name': 'Test owner',
            'type': 'C',
            'support_type': 'T',
            'contact_phone': '911234455',
            'year': 2017,
            'period_type': '1T',
            'date_start': '2017-01-01',
            'date_end': '2017-03-31',
            'previous_number': model349.name,
        })
        # Calculate
        _logger.debug('Calculate AEAT 349 1T 2017 - complementary')
        model349_c.button_calculate()
        e_record = model349_c.partner_record_ids.filtered(
            lambda x: x.operation_key == 'E')
        self.assertEqual(len(e_record), 1)
        self.assertEqual(e_record.total_operation_amount, 2400)
        a_record = model349_c.partner_record_ids.filtered(
            lambda x: x.operation_key == 'A')
        self.assertEqual(len(a_record), 1)
        self.assertEqual(a_record.total_operation_amount, 300)
        # Create a substitutive presentation for 1T 2017. We expect that all
        # records for 1T are proposed.
        model349_s = model349_model.create({
            'name': '3490000000003',
            'company_id': self.company.id,
            'company_vat': '1234567890',
            'contact_name': 'Test owner',
            'type': 'S',
            'support_type': 'T',
            'contact_phone': '911234455',
            'year': 2017,
            'period_type': '1T',
            'date_start': '2017-01-01',
            'date_end': '2017-03-31',
            'previous_number': model349.name,
        })
        # Calculate
        _logger.debug('Calculate AEAT 349 1T 2017 - substitutive')
        model349_s.button_calculate()
        e_record = model349_s.partner_record_ids.filtered(
            lambda x: x.operation_key == 'E')
        self.assertEqual(e_record.total_operation_amount, 4800)
        a_record = model349_s.partner_record_ids.filtered(
            lambda x: x.operation_key == 'A')
        self.assertEqual(a_record.total_operation_amount, 600)
        # Create a substitutive presentation for 2T 2017.
        # We create a refund of p1, and a new sale
        self._invoice_refund(p1, '2017-04-01')
        self._invoice_sale_create('2017-04-01')
        self._invoice_refund(s3, '2017-04-03')
        model349_2t = model349_model.create({
            'name': '3490000000004',
            'company_id': self.company.id,
            'company_vat': '1234567890',
            'contact_name': 'Test owner',
            'type': 'N',
            'support_type': 'T',
            'contact_phone': '911234455',
            'year': 2017,
            'period_type': '1T',
            'date_start': '2017-04-01',
            'date_end': '2017-06-30',
        })
        # Calculate
        _logger.debug('Calculate AEAT 349 2T 2017')
        model349_2t.button_calculate()
        self.assertEqual(model349_2t.total_partner_records, 1)
        self.assertEqual(model349_2t.total_partner_refunds, 2)
        self.assertEqual(model349_2t.total_partner_refunds_amount, 2700)
        e_record = model349_2t.partner_record_ids.filtered(
            lambda x: x.operation_key == 'E')
        self.assertEqual(e_record.total_operation_amount, 2400)
        a_records = model349_2t.partner_record_ids.filtered(
            lambda x: x.operation_key == 'A')
        self.assertEqual(len(a_records), 0)
        e_refunds = model349_2t.partner_refund_ids.filtered(
            lambda x: x.operation_key == 'E')
        self.assertEqual(len(e_refunds), 1)
        self.assertEqual(len(e_refunds.refund_detail_ids), 1)
        self.assertEqual(e_refunds.total_origin_amount, 4800)
        # total_origin_amount = Total amount partner in T1
        # total_operation_amount = T1 partner - refund (4800 - 2400) = 2400
        self.assertEqual(e_refunds.total_operation_amount, 2400)
        a_refund = model349_2t.partner_refund_ids.filtered(
            lambda x: x.operation_key == 'A')
        self.assertEqual(len(a_refund), 1)
        self.assertEqual(len(a_refund.refund_detail_ids), 2)
        # total_origin_amount = Total amount partner in T1
        self.assertEqual(a_refund.total_origin_amount, 600)
        # total_operation_amount = T1 partner - refund (600 - 300) = 300
        self.assertEqual(a_refund.total_operation_amount, 300)
        self.assertEqual(a_refund.period_type, model349_s.period_type)
        # Export to BOE
        export_to_boe = self.env['l10n.es.aeat.report.export_to_boe'].create({
            'name': 'test_export_to_boe.txt',
        })
        export_config_xml_ids = [
            'l10n_es_aeat_mod349.aeat_mod349_main_export_config',
        ]
        for xml_id in export_config_xml_ids:
            export_config = self.env.ref(xml_id)
            self.assertTrue(
                export_to_boe._export_config(model349, export_config)
            )

    def _create_349_report(self):
        return self.env['l10n.es.aeat.mod349.report'].sudo(
            self.account_manager).create({
                'name': '3490000000002',
                'company_id': self.company.id,
                'company_vat': '1234567890',
                'contact_name': 'Test owner',
                'type': 'N',
                'support_type': 'T',
                'contact_phone': '911234455',
                'year': 2017,
                'period_type': '1T',
                'date_start': '2017-01-01',
                'date_end': '2017-03-31',
            })

    def _create_349_refund(self, report, move_line, origin_amount, amounts):
        refund = self.env['l10n.es.aeat.mod349.partner_refund'].create({
            'report_id': report.id,
            'partner_id': self.customer.id,
            'partner_vat': self.customer.vat,
            'country_id': self.customer.country_id.id,
            'operation_key': 'E',
            'period_type': '1T',
            'year': 2017,
            'total_origin_amount': origin_amount,
        })
        for amount in amounts:
            self.env['l10n.es.aeat.mod349.partner_refund_detail'].create({
                'report_id': report.id,
                'refund_id': refund.id,
                'refund_line_id': move_line.id,
                'amount_untaxed': amount,
            })
        return refund

    def test_349_refund_rounding_residue(self):
        """A fully rectified operation must not block the report.

        Adding up the same decimal amounts in a different grouping leaves a
        binary floating point residue. That residue is negative and shows up
        as -0,00, and without rounding it fails the `>= 0.0` validity check,
        blocking the confirmation of an otherwise correct report.
        """
        self.customer.write({
            'vat': 'BE0411905847',
            'country_id': self.env.ref('base.be').id,
        })
        invoice = self._invoice_sale_create('2017-01-02')
        move_line = invoice.move_id.line_ids[0]
        report = self._create_349_report()
        # 489.10 * 3 == 1467.30 in decimal, but 1467.30 - (489.10 * 3) is
        # -2.27e-13 in binary floating point.
        residue_refund = self._create_349_refund(
            report, move_line, 1467.30, [489.10, 489.10, 489.10])
        self.assertEqual(residue_refund.total_operation_amount, 0.0)
        self.assertTrue(residue_refund.partner_refund_ok)
        self.assertFalse(residue_refund._get_invalid_reasons())
        # Also pin what the user reads in the summary: the reported symptom was
        # an amount rendered as -0,00, and no negative zero must reach it.
        self.assertEqual(
            '%.2f' % residue_refund.total_operation_amount, '0.00')
        # A genuinely negative amount must still be caught and explained
        negative_refund = self._create_349_refund(
            report, move_line, 1000.0, [489.10, 489.10, 489.10])
        self.assertAlmostEqual(
            negative_refund.total_operation_amount, -467.30, places=2)
        self.assertFalse(negative_refund.partner_refund_ok)
        self.assertTrue(negative_refund._get_invalid_reasons())
        report.partner_refund_ids = negative_refund
        with self.assertRaises(exceptions.Warning):
            report._check_report_lines()

    def test_349_partner_record_invalid_reasons(self):
        """A partner record explains why it is not valid, field by field"""
        self.customer.write({
            'vat': 'BE0411905847',
            'country_id': self.env.ref('base.be').id,
        })
        invoice = self._invoice_sale_create('2017-01-02')
        move_line = invoice.move_id.line_ids[0]
        report = self._create_349_report()
        record = self.env['l10n.es.aeat.mod349.partner_record'].create({
            'report_id': report.id,
            'partner_id': self.customer.id,
            'partner_vat': self.customer.vat,
            'country_id': self.customer.country_id.id,
            'operation_key': 'E',
        })
        # Without details the total is zero, which is a reason on its own
        self.assertFalse(record.partner_record_ok)
        self.assertEqual(len(record._get_invalid_reasons()), 1)
        self.env['l10n.es.aeat.mod349.partner_record_detail'].create({
            'report_id': report.id,
            'partner_record_id': record.id,
            'move_line_id': move_line.id,
            'amount_untaxed': 2400.0,
        })
        self.assertTrue(record.partner_record_ok)
        self.assertFalse(record._get_invalid_reasons())
        # Every missing field adds its own reason
        record.write({'partner_vat': False, 'country_id': False})
        self.assertFalse(record.partner_record_ok)
        self.assertEqual(len(record._get_invalid_reasons()), 2)
