# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    _logger.info("Recompute sale.order.line.shopinvader_delivery_state")
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["sale.order.line"].search([])._compute_shopinvader_delivery_state()
