# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas.category import (
    ShopinvaderCategory as BaseShopinvaderCategory,
)


class ShopinvaderCategory(BaseShopinvaderCategory, extends=True):
    seo_title: str | None = None
    meta_keywords: str | None = None
    meta_description: str | None = None

    @classmethod
    def from_shopinvader_category(cls, odoo_rec):
        obj = super().from_shopinvader_category(odoo_rec)
        obj.seo_title = odoo_rec.seo_title or None
        obj.meta_keywords = odoo_rec.meta_keywords or None
        obj.meta_description = odoo_rec.meta_description or None
        return obj
