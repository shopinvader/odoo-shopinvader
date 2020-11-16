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

    def _get_product_template_linked(self, links):
        left_links = links.filtered(
            lambda x: x.left_product_tmpl_id != self.record_id
        )
        right_links = links.filtered(
            lambda x: x.left_product_tmpl_id == self.record_id
        )
        left_link_tmpl_ids = left_links.mapped("left_product_tmpl_id").ids
        right_link_tmpl_ids = right_links.mapped("right_product_tmpl_id").ids
        linked_tmpl_ids = set(left_link_tmpl_ids).union(
            set(right_link_tmpl_ids)
        )

        return self.env["product.template"].browse(linked_tmpl_ids)

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
            linked_tmpl = self._get_product_template_linked(links)

            bindings = linked_tmpl.mapped("shopinvader_bind_ids")
            bindings = bindings.filtered(
                lambda x: x.backend_id == self.backend_id
                and x.lang_id == self.lang_id
            )
            variants = bindings.mapped("shopinvader_variant_ids").filtered(
                lambda x: x.main
            )
            res[code] = [{"id": variant.record_id.id} for variant in variants]
        return res

    def _product_link_code(self, link):
        """Normalize link code, default to `generic` when missing."""
        return slugify(link.type_id.code or "generic").replace("-", "_")


class ShopinvaderProduct(models.Model):
    _name = "shopinvader.product"
    _inherit = ["shopinvader.product", "shopinvader.product.link.mixin"]
