# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import io
import struct

from PIL import Image

from odoo.tests.common import SavepointCase, at_install, post_install

try:
    import qrcode  # noqa: F401
except ImportError:
    qrcode = None

QR_URL = (
    "https://www2.agenciatributaria.gob.es/wlpl/TIKE-CONT/ValidarQR"
    "?nif=B91304501&numserie=T-0001&fecha=01-01-2026&importe=12.10"
)


@at_install(False)
@post_install(True)
class TestVerifactuPos(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestVerifactuPos, cls).setUpClass()
        cls.company = cls.env.user.company_id
        cls.pos_config = cls.env.ref('point_of_sale.pos_config_main')

    def _set_company_vat(self, vat):
        partner = self.company.partner_id
        self.env.cr.execute(
            "UPDATE res_partner SET vat = %s WHERE id = %s",
            (vat or None, partner.id))
        self.env['res.partner'].invalidate_cache()
        self.env['pos.config'].invalidate_cache()

    def _ui_order(self, **extra):
        values = {
            'name': 'Order 00001-001-0001',
            'uid': '00001-001-0001',
            'user_id': self.env.uid,
            'pos_session_id': 1,
            'lines': False,
            'partner_id': False,
            'creation_date': '2026-01-01 10:00:00',
            'fiscal_position_id': False,
            'pricelist_id': False,
        }
        values.update(extra)
        return values

    def test_01_issuer_vat_strips_country_prefix(self):
        self._set_company_vat('ESB91304501')
        self.assertEqual(self.pos_config.verifactu_issuer_vat, 'B91304501')

    def test_02_issuer_vat_strips_prefix_with_dash(self):
        self._set_company_vat('ES-B91304501')
        self.assertEqual(self.pos_config.verifactu_issuer_vat, 'B91304501')

    def test_03_issuer_vat_strips_inner_dash(self):
        self._set_company_vat('B-91304501')
        self.assertEqual(self.pos_config.verifactu_issuer_vat, 'B91304501')

    def test_04_issuer_vat_empty(self):
        self._set_company_vat(False)
        self.assertFalse(self.pos_config.verifactu_issuer_vat)

    def test_05_verifactu_disabled_by_default(self):
        self.assertFalse(self.pos_config.verifactu_enabled)

    def test_06_order_fields_copies_qr_url(self):
        res = self.env['pos.order']._order_fields(
            self._ui_order(verifactu_qr_url=QR_URL))
        self.assertEqual(res.get('verifactu_qr_url'), QR_URL)

    def test_07_order_fields_without_qr_url(self):
        res = self.env['pos.order']._order_fields(self._ui_order())
        self.assertNotIn('verifactu_qr_url', res)

    def test_08_qr_image_is_png_with_expected_size(self):
        if qrcode is None:
            self.skipTest("qrcode library not available")
        order = self.env['pos.order'].new({'verifactu_qr_url': QR_URL})
        image = order._get_verifactu_qr_image()
        self.assertTrue(image)
        png = base64.b64decode(image)
        self.assertEqual(png[:4], b'\x89PNG')
        self.assertEqual(png[12:16], b'IHDR')
        width, height = struct.unpack('>II', png[16:24])
        self.assertEqual(width, height)
        self.assertGreaterEqual(width, 236)
        self.assertLessEqual(width, 320)

    def test_10_qr_image_is_dark_on_light(self):
        if qrcode is None:
            self.skipTest("qrcode library not available")
        order = self.env['pos.order'].new({'verifactu_qr_url': QR_URL})
        png = base64.b64decode(order._get_verifactu_qr_image())
        image = Image.open(io.BytesIO(png)).convert('L')
        self.assertEqual(image.getpixel((0, 0)), 255)
        first_dark = next(
            x for x in range(image.size[0]) if image.getpixel((x, x)) < 128)
        self.assertGreater(first_dark, 0)

    def test_09_qr_image_without_url(self):
        if qrcode is None:
            self.skipTest("qrcode library not available")
        order = self.env['pos.order'].new({})
        self.assertFalse(order._get_verifactu_qr_image())
