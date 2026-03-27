# Copyright 2026 FactorLibre
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(env.cr, "account_tax_group", "company_id"):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE account_tax_group
            ALTER COLUMN company_id DROP NOT NULL
            """,
        )
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE ir_model_fields
            SET required = false
            WHERE model = 'account.tax.group'
            AND name = 'company_id'
            """,
        )
