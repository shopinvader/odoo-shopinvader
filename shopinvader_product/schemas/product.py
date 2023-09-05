# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Any

from odoo.addons.extendable_fastapi import StrictExtendableBaseModel

from .category import ShortShopinvaderCategory


class ShopinvaderProduct(StrictExtendableBaseModel):
    name: str

    @classmethod
    def from_shopinvader_product(cls, odoo_rec):
        return cls.model_construct(name=odoo_rec.display_name)


class ShopinvaderProductPriceInfo(StrictExtendableBaseModel):
    value: float = 0
    tax_included: bool = False
    original_value: float = 0
    discount: float = 0


class ShopinvaderVariant(StrictExtendableBaseModel):
    id: int
    model: ShopinvaderProduct
    main: bool = False
    full_name: str | None = None
    short_name: str | None = None
    variant_count: int = 0
    categories: list[ShortShopinvaderCategory] = []
    sku: str | None = None
    variant_attributes: dict[str:Any] = {}
    price: dict[str:ShopinvaderProductPriceInfo] = {}

    @classmethod
    def from_shopinvader_variant(cls, odoo_rec, index=None):
        return cls.model_construct(
            id=odoo_rec.record_id,
            model=ShopinvaderProduct.from_shopinvader_product(
                odoo_rec.shopinvader_product_id
            ),
            main=odoo_rec.main,
            full_name=odoo_rec.name or None,
            short_name=odoo_rec.short_name or None,
            variant_count=odoo_rec.product_variant_count,
            categories=[
                ShortShopinvaderCategory.from_shopinvader_category(
                    shopinvader_category, index=index
                )
                for shopinvader_category in odoo_rec.shopinvader_categ_ids
            ],
            sku=odoo_rec.default_code or None,
            variant_attributes=odoo_rec.variant_attributes,
            price=odoo_rec.price,
        )
