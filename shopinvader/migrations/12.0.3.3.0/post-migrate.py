# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for backend in env["shopinvader.backend"].search(
        [("tech_name", "=", False)]
    ):
        backend._onchange_name()
        _logger.info(
            "Backend '%s' `tech_name` set automatically. "
            "Please check if it suits your env.",
            backend.name,
        )
