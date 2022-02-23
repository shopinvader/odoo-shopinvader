# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    se_module = env["ir.module.module"].search(
        [("name", "=", "shopinvader_search_engine"), ("state", "=", "installed")],
        limit=1,
    )
    glue_module = env["ir.module.module"].search(
        [("name", "=", "shopinvader_assortment_search_engine")],
        limit=1,
    )
    if se_module and glue_module.state == "uninstalled":
        glue_module.write({"state": "to install"})
        _logger.info(
            "Install module shopinvader_assortment_search_engine "
            "to not alter behavior on existing installations."
        )
    return
