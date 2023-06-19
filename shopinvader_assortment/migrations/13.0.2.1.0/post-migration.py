# Copyright 2023 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def type_change_shopinvader_backend_product_assortment(env):
    openupgrade.m2o_to_x2m(
        env.cr,
        env["shopinvader.backend"],
        "shopinvader_backend",
        "product_assortment_ids",
        openupgrade.get_legacy_name("product_assortment_id"),
    )


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(
        env.cr,
        "shopinvader_backend",
        openupgrade.get_legacy_name("product_assortment_id"),
    ):
        type_change_shopinvader_backend_product_assortment(env)
