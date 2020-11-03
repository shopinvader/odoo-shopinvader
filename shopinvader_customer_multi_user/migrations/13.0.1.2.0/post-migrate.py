# Copyright 2020 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger("shopinvader_customer_multi_user." + __name__)


def force_compute_main_partner(env):
    invader_partners = env["shopinvader.partner"].search(
        [("main_partner_id", "=", False)]
    )
    invader_partners._compute_main_partner_id()
    _logger.info("shopinvader.partner.main_partner_id computed.")


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    force_compute_main_partner(env)
