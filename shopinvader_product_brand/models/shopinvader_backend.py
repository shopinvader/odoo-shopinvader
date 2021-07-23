# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderBackend(models.Model):

    _inherit = "shopinvader.backend"

    nbr_brand = fields.Integer(compute="_compute_nbr_content")

    def _to_compute_nbr_content(self):
        res = super()._to_compute_nbr_content()
        res["nbr_brand"] = "shopinvader.brand"
        return res

    def bind_all_brands(self, domain=None):
        domain = domain or [("product_ids.shopinvader_bind_ids", "!=", False)]
        result = self._bind_all_content(
            "product.brand",
            "shopinvader.brand",
            domain,
        )
        return result
