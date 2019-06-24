# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

try:
    from openupgradelib import openupgrade
except (ImportError, IOError) as err:
    _logger.debug(err)


def pre_init_hook(cr):
    """
    Rename the module 'shopinvader_stock' into 'shopinvader_product_stock'.
    :param cr: database cursor
    :return:
    """
    openupgrade.update_module_names(
        cr,
        [("shopinvader_stock", "shopinvader_product_stock")],
        merge_modules=True,
    )


def post_init_hook(cr, registry):
    """
    Set default value for warehouse_ids on shopinvader.backend
    """
    env = api.Environment(cr, SUPERUSER_ID, dict())
    for backend in env["shopinvader.backend"].search(
        [("warehouse_ids", "=", False)]
    ):
        warehouse = env["stock.warehouse"].search(
            [
                "|",
                ("company_id", "=", backend.company_id.id),
                ("company_id", "=", False),
            ],
            limit=1,
        )
        backend.warehouse_ids = warehouse
