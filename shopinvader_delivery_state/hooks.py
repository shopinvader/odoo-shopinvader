# Copyright 2021 Camptocamp SA (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    _logger.info("Recompute sale.order.shopinvader_state")
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["sale.order"].search([])._compute_shopinvader_state()
