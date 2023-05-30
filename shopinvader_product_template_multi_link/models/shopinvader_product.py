# Copyright 2017 Akretion (http://www.akretion.com).
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# Copyright (C) 2020 (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ShopinvaderProduct(models.Model):
    _name = "shopinvader.product"
    _inherit = [
        "shopinvader.product",
        "shopinvader.product.link.mixin",
    ]

    def _product_link_target(self, link):
        if link.left_product_tmpl_id == self.record_id:
            return link.right_product_tmpl_id
        elif link.type_id.is_symmetric:
            return link.left_product_tmpl_id

    def _product_link_target_variant(self, target):
        """Retrieve variant for given template

        :return: set
        """
        for shopinvader_variant in target.shopinvader_bind_ids.shopinvader_variant_ids:
            # Get bindings of the correct backend and lang, pick only the main one
            if (
                shopinvader_variant.backend_id == self.backend_id
                and shopinvader_variant.lang_id == self.lang_id
                and shopinvader_variant.main
            ):
                return shopinvader_variant
