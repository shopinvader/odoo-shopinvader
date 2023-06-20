# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    cr.execute("SELECT name FROM ir_module_module WHERE name='sale_cart_rest_api';")
    if cr.fetchall():
        _logger.info("Rename sale_cart_rest_api to shopinvader_api_cart")
        openupgrade.update_module_names(
            cr, [("sale_cart_rest_api", "shopinvader_api_cart")], True
        )
