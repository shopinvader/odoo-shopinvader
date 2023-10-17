# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo.addons.http_routing.models.ir_http import slugify
from odoo.addons.shopinvader_product import schemas

from ..models.product_product import LinkPosition
from .product_link import ProductLink


class ProductProduct(schemas.ProductProduct, extends=True):
    links: dict[str, list[ProductLink]] = {}

    @classmethod
    def from_product_product(cls, odoo_rec):
        res = super().from_product_product(odoo_rec)
        res.links = res._compute_links(odoo_rec)
        return res

    def _compute_links(self, odoo_rec):
        """We add a link info for symmetrical link or the left part of
        asymmetrical link. This is done on purpose since we take as granted
        that the right part of asymmetrical link means that we don't want to
        promote the left part as the left part is less important than the right part.
        """
        res = defaultdict(list)
        for (key, product_ids) in odoo_rec.shopinvader_product_links.items():
            position, link_type_id = key
            link_type = odoo_rec.env["product.template.link.type"].browse(link_type_id)
            if position == LinkPosition.LEFT or link_type.is_symmetric:
                products = odoo_rec.env["product.product"].browse(list(product_ids))
                code = self._normalize_product_link_code(link_type.code)
                res[code].extend(
                    ProductLink.from_product_product(product)
                    for product in products.sorted("id")
                )
        return res

    def _normalize_product_link_code(self, code):
        """Normalize link code, default to `generic` when missing."""
        return slugify(code or "generic").replace("-", "_")
