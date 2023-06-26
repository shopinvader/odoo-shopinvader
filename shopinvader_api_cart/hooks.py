# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def _rename_applied_transaction_uuids(env):
    openupgrade.rename_fields(
        env,
        [
            (
                "sale.order",
                "sale_order",
                "applied_transaction_uuids",
                "applied_cart_api_transaction_uuids",
            )
        ],
    )


def pre_init_hook(cr):
    cr.execute("SELECT name FROM ir_module_module WHERE name='sale_cart_rest_api';")
    if cr.fetchall():
        _logger.info("Rename sale_cart_rest_api to shopinvader_api_cart")
        openupgrade.update_module_names(
            cr, [("sale_cart_rest_api", "shopinvader_api_cart")], True
        )

    # Rename applied_transaction_uuids -> applied_cart_api_transaction_uuids
    # Nothing done if column doesn't exist
    env = api.Environment(cr, SUPERUSER_ID, {})
    _rename_applied_transaction_uuids(env)
