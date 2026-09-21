# Copyright 2022 Studio73 - Ethan Hildick <ethan@studio73.es>
# Copyright 2022 Tecnativa - Víctor Martínez
# Copyright 2023 Factor Libre - Aritz Olea
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class L10nEsAeatMod369LineGrouped(models.Model):
    _name = "l10n.es.aeat.mod369.line.grouped"
    _description = "Grouped info by country for 369 model"

    mod369_line_ids = fields.Many2many(
        string="Mod369 lines",
        comodel_name="l10n.es.aeat.mod369.line",
    )
    refund_line_ids = fields.Many2many(
        string="Refund lines",
        relation="refund_line_id_rel",
        comodel_name="account.move.line",
    )
    report_id = fields.Many2one(
        string="Mod369 report", comodel_name="l10n.es.aeat.mod369.report"
    )
    country_id = fields.Many2one(string="Country", comodel_name="res.country")
    oss_country_id = fields.Many2one(string="OSS Country", comodel_name="res.country")
    country_code = fields.Char(
        string="Country code", compute="_compute_country_code", store=True
    )
    tax_id = fields.Many2one(string="Tax", comodel_name="account.tax")
    vat_type = fields.Float(string="VAT Type", related="tax_id.amount")
    vat_type_str = fields.Char(compute="_compute_vat_type_str")
    service_type = fields.Selection(
        related="tax_id.service_type",
        string="Service type",
    )
    base = fields.Float(string="Base total")
    base_str = fields.Char(compute="_compute_base_str")
    amount = fields.Float(string="Amount total")
    amount_str = fields.Char(compute="_compute_amount_str")
    is_refund = fields.Boolean()
    refund_fiscal_year = fields.Integer()
    refund_period = fields.Char()
    tax_correction = fields.Float()
    tax_correction_str = fields.Char(compute="_compute_tax_correction_str")
    # page 8 fields
    is_page_8_line = fields.Boolean(
        string="Is part of page 8", help="Used to filter for grouped lines for page 8"
    )
    page_3_total = fields.Float(string="Spanish services")
    page_4_total = fields.Float(string="Spanish goods")
    page_3_4_total = fields.Float(string="Spanish services and goods")
    page_5_total = fields.Float(string="Non-Spanish services")
    page_6_total = fields.Float(string="Non-Spanish goods")
    page_5_6_total = fields.Float(string="Non-Spanish services and goods")
    pos_corrections = fields.Float(string="Positive corrections")
    neg_corrections = fields.Float(string="Negative corrections")
    result_total = fields.Float(string="Total result")
    total_deposit = fields.Float(string="Total to deposit ES")
    total_return = fields.Float(string="Total to return EM")

    @api.depends("vat_type")
    def _compute_vat_type_str(self):
        for line in self:
            vat_type_split = str(line.vat_type).split(".")
            line.vat_type_str = vat_type_split[0].zfill(3) + vat_type_split[1].ljust(
                2, "0"
            )

    @api.depends("base")
    def _compute_base_str(self):
        for line in self:
            base_split = str(line.base).split(".")
            line.base_str = base_split[0].zfill(15) + base_split[1].ljust(2, "0")

    @api.depends("amount")
    def _compute_amount_str(self):
        for line in self:
            amount_split = str(line.amount).split(".")
            line.amount_str = amount_split[0].zfill(15) + amount_split[1].ljust(2, "0")

    @api.depends("tax_correction")
    def _compute_tax_correction_str(self):
        for line in self:
            tax_correction_split = str(line.tax_correction).split(".")
            integer_part = tax_correction_split[0].zfill(15)
            decimal_part = tax_correction_split[1].ljust(2, "0")
            line.tax_correction_str = integer_part + decimal_part

    @api.depends("oss_country_id", "oss_country_id.code")
    def _compute_country_code(self):
        # The l10n_es_aeat helper (_map_aeat_country_code) maps AEAT -> ISO,
        # the opposite direction to the one needed here, so the ISO -> AEAT
        # mapping is applied locally. It only differs for Greece, which AEAT
        # codes as EL.
        iso_to_aeat = {"GR": "EL"}
        for line in self:
            code = line.oss_country_id.code
            line.country_code = iso_to_aeat.get(code, code)

    def get_calculated_move_lines(self):
        res = self.env.ref("account.action_account_moves_all_a").sudo().read()[0]
        view = self.env.ref("l10n_es_aeat.view_move_line_tree")
        res["views"] = [(view.id, "tree")]
        move_lines = self.mapped("mod369_line_ids.tax_line_id.move_line_ids")
        # The corrections of earlier periods are the ones `calculate()` already
        # set aside on page 7. Subtracting them keeps the rule in one place and
        # spares walking every journal item of the period to tell them apart.
        corrections = self.mapped("report_id.refund_line_ids.refund_line_ids")
        res["domain"] = [("id", "in", (move_lines - corrections).ids)]
        return res

    def get_calculated_refund_move_lines(self):
        res = self.env.ref("account.action_account_moves_all_a").sudo().read()[0]
        view = self.env.ref("l10n_es_aeat.view_move_line_tree")
        res["views"] = [(view.id, "tree")]
        res["domain"] = [("id", "in", self.mapped("refund_line_ids").ids)]
        return res
