/* Copyright 2016 David Gómez Quilón <david.gomez@aselcis.com>
   Copyright 2018-19 Tecnativa - David Vidal
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/

odoo.define("l10n_es_pos.models", function (require) {
    "use strict";

    const {PosGlobalState, Order} = require("point_of_sale.models");
    const Registries = require("point_of_sale.Registries");

    const L10NESGlobalState = (PosGlobalState) =>
        class L10NESGlobalState extends PosGlobalState {
            constructor() {
                super(...arguments);
                this.pushed_simple_invoices = [];

                this.own_simplified_invoice_prefix = ""; // Unique UUID
            }
            get_simple_inv_next_number() {
                return this.env.services.rpc({
                    method: "search_read",
                    domain: [["id", "=", this.env.pos.config.id]],
                    fields: ["l10n_es_simplified_invoice_number"],
                    model: "pos.config",
                });
            }
            get_padding_simple_inv(number) {
                const diff =
                    this.config.l10n_es_simplified_invoice_padding -
                    number.toString().length;
                let result = "";
                if (diff <= 0) {
                    result = number;
                } else {
                    for (let i = 0; i < diff; i++) {
                        result += "0";
                    }
                    result += number;
                }
                return result;
            }
            push_simple_invoice(order) {
                if (
                    this.pushed_simple_invoices.indexOf(
                        order.data.l10n_es_unique_id
                    ) === -1
                ) {
                    this.pushed_simple_invoices.push(order.data.l10n_es_unique_id);
                    ++this.config.l10n_es_simplified_invoice_number;
                }
            }
            _flush_orders(orders) {
                var self = this;
                // Save pushed orders numbers
                _.each(orders, function (order) {
                    if (!order.data.to_invoice) {
                        self.push_simple_invoice(order);
                    }
                });
                return super._flush_orders(...arguments);
            }
        };
    Registries.Model.extend(PosGlobalState, L10NESGlobalState);

    const L10NESOrder = (Order) =>
        class L10NESOrder extends Order {
            get_total_with_tax() {
                const total = super.get_total_with_tax(...arguments);
                const below_limit =
                    total <= this.pos.config.l10n_es_simplified_invoice_limit;
                this.is_simplified_invoice =
                    below_limit && this.pos.config.iface_l10n_es_simplified_invoice;
                return total;
            }
            set_simple_inv_number() {
                const self = this;
                return this.pos
                    .get_simple_inv_next_number()
                    .then(function (configs) {
                        const config = configs[0];
                        self.pos.config.l10n_es_simplified_invoice_number =
                            config.l10n_es_simplified_invoice_number;
                        const simplified_invoice_number =
                            self.pos.config.l10n_es_simplified_invoice_prefix +
                            self.pos.get_padding_simple_inv(
                                config.l10n_es_simplified_invoice_number
                            );
                        self.l10n_es_unique_id = simplified_invoice_number;
                        self.is_simplified_invoice = true;
                    })
                    .catch(function () {
                        self.l10n_es_unique_id = self.uid;
                        self.is_simplified_invoice = true;
                    });
            }
            get_base_by_tax() {
                const base_by_tax = {};
                this.get_orderlines().forEach(function (line) {
                    const tax_detail = line.get_tax_details();
                    const base_price = line.get_price_without_tax();
                    if (tax_detail) {
                        Object.keys(tax_detail).forEach(function (tax) {
                            if (Object.keys(base_by_tax).includes(tax)) {
                                base_by_tax[tax] += base_price;
                            } else {
                                base_by_tax[tax] = base_price;
                            }
                        });
                    }
                });
                return base_by_tax;
            }
            init_from_JSON(json) {
                super.init_from_JSON(...arguments);
                this.to_invoice = json.to_invoice;
                this.l10n_es_unique_id = json.l10n_es_unique_id;
            }
            export_as_JSON() {
                const res = super.export_as_JSON(...arguments);
                res.to_invoice = this.is_to_invoice();
                if (!res.to_invoice) {
                    res.l10n_es_unique_id = this.l10n_es_unique_id;
                }
                return res;
            }
            export_for_printing() {
                const result = super.export_for_printing(...arguments);
                const company = this.pos.company;
                result.l10n_es_unique_id = this.l10n_es_unique_id;
                result.to_invoice = this.to_invoice;
                result.company.street = company.street;
                result.company.zip = company.zip;
                result.company.city = company.city;
                result.company.state_id = company.state_id;
                const base_by_tax = this.get_base_by_tax();
                for (const tax of result.tax_details) {
                    tax.base = base_by_tax[tax.tax.id];
                }
                return result;
            }
        };
    Registries.Model.extend(Order, L10NESOrder);
});
