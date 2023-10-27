# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

from odoo.addons.shopinvader_api_cart import (  # pylint: disable=odoo-addons-relative-import
    hooks,
)

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info(
        "Renaming sale.order field 'applied_transaction_uuids' "
        "to 'applied_cart_api_transaction_uuids'"
    )
    hooks._rename_applied_transaction_uuids(env)
