# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel

from odoo.addons.shopinvader_product.schemas import ProductProduct as BaseProduct


class ProductTemplatePriceInfo(StrictExtendableBaseModel):
    value: float = 0
    tax_included: bool = False
    original_value: float = 0
    discount: float = 0


class ProductProduct(BaseProduct, extends=True):
    price: dict[str, ProductTemplatePriceInfo] = {}

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.price = odoo_rec.shopinvader_price or None
        return obj
