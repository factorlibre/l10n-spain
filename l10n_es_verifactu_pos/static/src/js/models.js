/* Copyright 2026 FactorLibre
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/

/* global QRCode */
odoo.define('l10n_es_verifactu_pos.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');

    var QR_TARGET_PX = 280;
    var QR_MIN_PX = 240;
    var QR_MAX_PX = 320;
    var QR_MARGIN = 4;

    var _super_Order = models.Order.prototype;
    models.Order = models.Order.extend({
        verifactu_is_applicable: function () {
            return Boolean(
                this.pos.config.verifactu_enabled &&
                this.pos.config.verifactu_issuer_vat &&
                this.simplified_invoice &&
                !this.is_to_invoice()
            );
        },
        verifactu_get_amount: function () {
            var amount = this.get_total_with_tax();
            if (Math.abs(amount) < 0.005) {
                amount = 0;
            }
            return amount.toFixed(2);
        },
        verifactu_build_url: function (date) {
            var base_url = (this.pos.config.verifactu_base_url || '').trim();
            var params = [
                ['nif', this.pos.config.verifactu_issuer_vat || ''],
                ['numserie', this.simplified_invoice],
                ['fecha', date],
                ['importe', this.verifactu_get_amount()],
            ];
            var query = params.map(function (param) {
                return param[0] + '=' + encodeURIComponent(param[1]);
            }).join('&');
            return base_url + '?' + query;
        },
        verifactu_render_qr: function (url) {
            var options = {errorCorrectionLevel: 'M', margin: QR_MARGIN};
            var margins = 2 * QR_MARGIN;
            var modules = QRCode.create(url, options).modules.size + margins;
            options.scale = this.verifactu_qr_scale(modules);
            var data_url = false;
            QRCode.toDataURL(url, options, function (error, result) {
                if (!error) {
                    data_url = result;
                }
            });
            return data_url;
        },
        verifactu_qr_scale: function (modules) {
            var best = Math.max(1, Math.floor(QR_MAX_PX / modules));
            for (var scale = 1; modules * scale <= QR_MAX_PX; scale++) {
                var size = modules * scale;
                var best_size = modules * best;
                var closer = Math.abs(size - QR_TARGET_PX) <
                    Math.abs(best_size - QR_TARGET_PX);
                if (size >= QR_MIN_PX && (best_size < QR_MIN_PX || closer)) {
                    best = scale;
                }
            }
            return best;
        },
        verifactu_generate_qr: function () {
            this.verifactu_qr = false;
            this.verifactu_qr_url = false;
            if (!this.verifactu_is_applicable()) {
                return;
            }
            this.verifactu_date = moment(
                this.validation_date || this.creation_date
            ).format('DD-MM-YYYY');
            try {
                var url = this.verifactu_build_url(this.verifactu_date);
                this.verifactu_qr = this.verifactu_render_qr(url);
                this.verifactu_qr_url = url;
            } catch (error) {
                console.error('VERI*FACTU QR generation failed', error);
            }
        },
        initialize_validation_date: function () {
            _super_Order.initialize_validation_date.apply(this, arguments);
            this.verifactu_generate_qr();
        },
        init_from_JSON: function (json) {
            _super_Order.init_from_JSON.apply(this, arguments);
            this.verifactu_qr_url = json.verifactu_qr_url;
            this.verifactu_qr = json.verifactu_qr;
            this.verifactu_date = json.verifactu_date;
        },
        export_as_JSON: function () {
            var res = _super_Order.export_as_JSON.apply(this, arguments);
            if (this.verifactu_qr_url && this.verifactu_is_applicable()) {
                res.verifactu_qr_url = this.verifactu_qr_url;
                res.verifactu_qr = this.verifactu_qr;
                res.verifactu_date = this.verifactu_date;
            }
            return res;
        },
        export_for_printing: function () {
            var res = _super_Order.export_for_printing.apply(this, arguments);
            var applicable = this.verifactu_is_applicable();
            res.verifactu_qr = applicable && this.verifactu_qr;
            res.verifactu_qr_url = applicable && this.verifactu_qr_url;
            return res;
        },
    });

});
