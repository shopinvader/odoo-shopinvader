# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas import ProductProduct as BaseProduct

from .images_mixin import ImageMixin


class ProductProduct(BaseProduct, ImageMixin, extends=True):
    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        if odoo_rec.variant_image_ids:
            obj._fill_image_from_image_relation_mixin(odoo_rec, "variant_image_ids")
        return obj
