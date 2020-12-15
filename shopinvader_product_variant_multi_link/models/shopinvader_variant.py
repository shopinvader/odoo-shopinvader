# Copyright (C) 2020 (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ShopinvaderVariant(models.Model):
    _name = "shopinvader.variant"
    _inherit = ["shopinvader.variant", "shopinvader.product.link.mixin"]

    def _get_product_links(self):
        return self.product_variant_link_ids

    def _product_link_target(self, link):
        if link.left_product_id == self.record_id:
            return link.right_product_id
        elif link.type_id.is_symmetric:
            return link.left_product_id

    def _product_link_target_variant(self, target):
        return target._get_invader_variant(self.backend_id, self.lang_id.code)
