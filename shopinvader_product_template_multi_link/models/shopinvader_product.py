# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# Copyright (C) 2020 (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from collections import defaultdict

from odoo import fields, models

_logger = logging.getLogger(__name__)

try:
    from slugify import slugify
except ImportError:
    _logger.debug("Cannot `import slugify`.")


class ShopinvaderProductLinkMixin(models.AbstractModel):
    _name = "shopinvader.product.link.mixin"
    _description = "Shopinvader product link mixin"

    product_links = fields.Serialized(
        string="Product template links", compute="_compute_product_links"
    )

    def _compute_product_links(self):
        for record in self:
            record.product_links = record._get_product_links_by_type(
                record._get_product_links()
            )

    def _get_product_links(self):
        return self.product_template_link_ids

    def _get_product_links_by_type(self, links):
        """Retrieve variants as list of ids by link type.

        Eg: {"up_selling": [{id: 1}, {id: 2}, {id: 3}]}

        :return: dict
        """
        self.ensure_one()
        grouped = defaultdict(self.env["product.template.link"].browse)
        for link in links:
            code = self._product_link_code(link)
            grouped[code] |= link
        res = {}
        for code, links in grouped.items():
            res[code] = [self._get_product_link_data(x) for x in links]
        return res

    def _product_link_code(self, link):
        """Normalize link code, default to `generic` when missing."""
        return slugify(link.type_id.code or "generic").replace("-", "_")

    def _get_product_link_data(self, link):
        target = self._product_link_target(link)
        variant = self._product_link_target_variant(target)
        if variant:
            return {"id": variant.record_id.id}
        return {}

    def _product_link_target(self, link):
        """Retrieve the target of the link."""
        raise NotImplementedError()

    def _product_link_target_variant(self, target):
        """Retrieve variant ids for given target product

        :return: set
        """
        raise NotImplementedError()


class ShopinvaderProduct(models.Model):
    _name = "shopinvader.product"
    _inherit = ["shopinvader.product", "shopinvader.product.link.mixin"]

    def _product_link_target(self, link):
        if link.left_product_tmpl_id != self.record_id:
            return link.left_product_tmpl_id
        else:
            return link.right_product_tmpl_id

    def _product_link_target_variant(self, target):
        """Retrieve variant for given template

        :return: set
        """
        for shopinvader_variant in target.mapped(
            "shopinvader_bind_ids.shopinvader_variant_ids"
        ):
            # Get bindings of the correct backend and lang, pick only the main one
            if (
                shopinvader_variant.backend_id == self.backend_id
                and shopinvader_variant.lang_id == self.lang_id
                and shopinvader_variant.main
            ):
                return shopinvader_variant
