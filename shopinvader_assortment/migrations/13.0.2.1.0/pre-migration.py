# Copyright 2023 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_renames = {
    "shopinvader_backend": [("product_assortment_id", None)],
}


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(
        env.cr, "shopinvader_backend", "product_assortment_id"
    ):
        openupgrade.rename_columns(env.cr, _column_renames)
