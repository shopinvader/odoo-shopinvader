# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Upgrade shopinvader_cart_expiry: update cron")
    if not version:
        return
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        cron = env.ref(
            "shopinvader_cart_expiry.ir_cron_shopinvader_cart_expiry",
            raise_if_not_found=False,
        )
        if cron:
            cron.write({"code": "model._scheduler_manage_cart_expiry()"})
    return
