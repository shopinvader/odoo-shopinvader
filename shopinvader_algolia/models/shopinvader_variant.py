# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    @api.model
    def _get_facetting_values(self, se_bakend):
        default = [
            "categories.id",
            "Categories.lvl0hierarchical",
            "Categories.lvl1hierarchical",
            "Categories.lvl2hierarchical",
            "main",
            "redirect_url_key",
            "url_key",
            "sku",
            "price.default.value",
        ]
        invader_backend = self.env["shopinvader.backend"].search(
            [("se_backend_id", "=", se_bakend.id)]
        )
        filters = invader_backend.filter_ids
        filter_facetting_values = [f.display_name for f in filters]
        return default + filter_facetting_values
