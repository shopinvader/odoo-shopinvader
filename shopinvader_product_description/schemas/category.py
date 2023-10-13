# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas import (
    ProductCategory as BaseProductCategory,
)


class ProductCategory(BaseProductCategory, extends=True):
    subtitle: str | None = None
    description: str | None = None
    short_description: str | None = None

    @classmethod
    def from_product_category(cls, odoo_rec):
        obj = super().from_product_category(odoo_rec)
        obj.subtitle = odoo_rec.subtitle or None
        obj.description = odoo_rec.description or None
        obj.short_description = odoo_rec.short_description or None
        return obj
