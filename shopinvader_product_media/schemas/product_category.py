# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas import (
    ProductCategory as BaseProductCategory,
)

from . import MediaData


class ProductCategory(BaseProductCategory, extends=True):
    media: list[MediaData] = []

    @classmethod
    def from_product_category(cls, odoo_rec):
        obj = super().from_product_category(odoo_rec)
        obj.media = [MediaData.from_media_data(m) for m in odoo_rec.media_ids]
        return obj
