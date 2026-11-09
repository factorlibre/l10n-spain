# Copyright 2026 FactorLibre - Aritz Olea
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    is_bankrupcy_uncollectible_debt = fields.Boolean(
        string="Bankrupcy/uncollectible debt",
        help="When this is set, the tax base and rate will "
        "be reflected in fields 31, 32, 45 and 46 of the AEAT 390 model",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    def action_move_create(self):
        """The 390 report reads the flag from the journal entry."""
        res = super().action_move_create()
        self.filtered("is_bankrupcy_uncollectible_debt").mapped("move_id").write(
            {"is_bankrupcy_uncollectible_debt": True}
        )
        return res
