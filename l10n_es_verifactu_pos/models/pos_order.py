# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import logging
from io import BytesIO

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

try:
    import qrcode
except (ImportError, IOError) as err:  # pragma: no cover
    _logger.debug(err)

VERIFACTU_QR_TARGET_PX = 280
VERIFACTU_QR_MIN_PX = 240
VERIFACTU_QR_MAX_PX = 320
VERIFACTU_QR_BORDER = 4


def verifactu_qr_scale(modules):
    """Integer pixels per module giving a 30-40 mm QR at 8 dots/mm."""
    scales = [
        scale for scale in range(1, VERIFACTU_QR_MAX_PX // modules + 1)
        if modules * scale >= VERIFACTU_QR_MIN_PX
    ]
    if not scales:
        return max(1, VERIFACTU_QR_MAX_PX // modules)
    return min(
        scales, key=lambda s: abs(modules * s - VERIFACTU_QR_TARGET_PX))


class PosOrder(models.Model):
    _inherit = "pos.order"

    verifactu_qr_url = fields.Char(
        string="VERI*FACTU QR URL",
        readonly=True,
        copy=False,
    )

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        if ui_order.get("verifactu_qr_url"):
            res["verifactu_qr_url"] = ui_order["verifactu_qr_url"]
        return res

    @api.multi
    def _get_verifactu_qr_image(self):
        """PNG (base64 str) of the VERI*FACTU QR code, or False."""
        self.ensure_one()
        if not self.verifactu_qr_url:
            return False
        try:
            qr = qrcode.QRCode(
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                border=VERIFACTU_QR_BORDER,
            )
            qr.add_data(self.verifactu_qr_url)
            qr.make(fit=True)
            modules = qr.modules_count + 2 * VERIFACTU_QR_BORDER
            qr.box_size = verifactu_qr_scale(modules)
            image = qr.make_image()
            buffer = BytesIO()
            image.save(buffer, format="PNG")
        except NameError:
            _logger.debug("The qrcode library is not available.")
            return False
        return base64.b64encode(buffer.getvalue()).decode()
