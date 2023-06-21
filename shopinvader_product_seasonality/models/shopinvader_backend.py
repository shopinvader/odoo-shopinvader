# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ShopinvaderBackend(models.Model):

    _inherit = "shopinvader.backend"

    def bind_all_seasonal_config_lines(self, domain=None):
        domain = domain or [("product_id.shopinvader_bind_ids", "!=", False)]
        result = self._bind_all_content(
            "seasonal.config.line",
            "shopinvader.seasonal.config.line",
            domain,
            langs="none",
        )
        return result
