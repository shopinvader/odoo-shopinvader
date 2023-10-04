# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product_brand.schemas import (
    ProductBrand as BaseProductBrand,
)
from odoo.addons.shopinvader_search_engine_image.schemas import ImageMixin


class ProductBrand(BaseProductBrand, ImageMixin, extends=True):
    @classmethod
    def from_product_brand(cls, odoo_rec):
        obj = super().from_product_brand(odoo_rec)
        obj._fill_image_from_image_relation_mixin(odoo_rec, "image_ids")
        return obj
