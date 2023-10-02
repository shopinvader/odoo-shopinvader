# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas import (
    ProductTemplate as BaseProductTemplate,
)

from . import ProductBrand


class ProductTemplate(BaseProductTemplate, extends=True):
    brand: ProductBrand | None = None

    @classmethod
    def from_product_template(cls, odoo_rec):
        obj = super().from_product_template(odoo_rec)
        obj.brand = (
            ProductBrand.from_product_brand(odoo_rec.product_brand_id)
            if odoo_rec.product_brand_id
            else None
        )
        return obj
