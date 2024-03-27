# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict
from enum import IntEnum

from odoo import api, fields, models


class LinkPosition(IntEnum):
    LEFT = 1
    RIGHT = 2


class ProductProduct(models.Model):
    _inherit = "product.product"

    # we use a Binary field to store a computed object that will never be stored
    # into the database. The binary field is the only field that preserve the
    # original type as value for the cache. We must therefore pay attention to
    # the type of the value we store in this field (enum and ids only).
    shopinvader_product_links = fields.Binary(
        string="Shopinvader Product Template Links",
        compute="_compute_shopinvader_product_links",
        help="A dictionary where key is tuple of (LinkPosition,link type id) and "
        "value is a set of variant ids linked to the product. Only "
        "active links are returned if target variants are also into"
        "the same search engine index.",
        store=False,
        attachment=False,
    )

    @api.depends("product_tmpl_id.product_template_link_ids")
    def _compute_shopinvader_product_links(self):
        """Compute the shopinvader product links.

        The result is a dictionary where key is tuple of (LinkPosition,link type id) and
        value is a set of variant ids linked to the product. Only active links
        are returned if target variants are also into the same search engine index.
        """
        for record in self:
            links = self.product_template_link_ids
            res = defaultdict(set)
            for link in links:
                position, target = self._get_target(link)
                if not target:
                    continue
                res[(position, link.type_id.id)].add(target.id)
            record.shopinvader_product_links = res

    def _get_target(self, link) -> tuple[LinkPosition, "ProductProduct"]:
        """Return the target main variant of the current product for the link.

        :param link: product template link
        :return: tuple(LinkPosition, ProductProduct) The position of the current
                product in the link and the target variant. The position is important
                because it allows to know to interpret the link according to its type.
        """
        self.ensure_one()
        if link.left_product_tmpl_id == self.product_tmpl_id:
            position = LinkPosition.LEFT
            target = link.right_product_tmpl_id
        else:
            position = LinkPosition.RIGHT
            target = link.left_product_tmpl_id
        return position, self._get_main_product_bound(target.product_variant_ids)

    def _get_main_product_bound(self, products):
        """Return the main bound product of the current product"""
        self.ensure_one()
        return products.filtered(lambda p: p.main)._filter_by_index()
