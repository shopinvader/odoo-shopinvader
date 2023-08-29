# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas.category import (
    ProductCategory as BaseProductCategory,
    ShortProductCategory as BaseShortProductCategory,
)


class ShortProductCategory(BaseShortProductCategory, extends=True):
    url_key: str | None = None

    @classmethod
    def from_product_category(cls, odoo_rec, *args, **kwargs):
        obj = super().from_product_category(odoo_rec, *args, **kwargs)
        obj.url_key = odoo_rec.url_key or None
        return obj


class ProductCategory(BaseProductCategory, extends=True):
    redirect_url_key: list[str] = []

    @classmethod
    def from_product_category(cls, odoo_rec):
        obj = super().from_product_category(odoo_rec)
        obj.redirect_url_key = odoo_rec.redirect_url_key
        return obj
