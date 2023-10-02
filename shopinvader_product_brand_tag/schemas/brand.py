# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product_brand.schemas import (
    ProductBrand as BaseProductBrand,
)

from . import ProductBrandTag


class ProductBrand(BaseProductBrand):
    tags: list[ProductBrandTag] = []

    @classmethod
    def from_product_brand(cls, odoo_rec):
        obj = super().from_product_brand(odoo_rec)
        obj.tags = [
            ProductBrandTag.from_product_brand_tag(tag) for tag in odoo_rec.tag_ids
        ]
        return obj
