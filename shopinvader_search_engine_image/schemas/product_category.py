# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas import ProductCategory as BaseCategory

from .images_mixin import ImageMixin


class ProductCategory(BaseCategory, ImageMixin, extends=True):
    @classmethod
    def from_product_category(cls, odoo_rec):
        obj = super().from_product_category(odoo_rec)
        obj._fill_image_from_image_relation_mixin(odoo_rec, "image_ids")
        return obj
