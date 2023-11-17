# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas import ProductProduct as BaseProductProduct

from . import MediaData


class ProductProduct(BaseProductProduct, extends=True):
    medias: list[MediaData] = []

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.medias = [MediaData.from_media_data(m) for m in odoo_rec.variant_media_ids]
        return obj
