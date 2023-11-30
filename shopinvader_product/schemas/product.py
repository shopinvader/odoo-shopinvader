# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Any

from extendable_pydantic import StrictExtendableBaseModel

from .category import ShortProductCategory


class ProductTemplate(StrictExtendableBaseModel):
    name: str

    @classmethod
    def from_product_template(cls, odoo_rec):
        return cls.model_construct(name=odoo_rec.display_name)


class ProductTemplatePriceInfo(StrictExtendableBaseModel):
    value: float = 0
    tax_included: bool = False
    original_value: float = 0
    discount: float = 0


class ProductProduct(StrictExtendableBaseModel):
    id: int
    model: ProductTemplate
    main: bool = False
    name: str | None = None
    short_name: str | None = None
    variant_count: int = 0
    categories: list[ShortProductCategory] = []
    sku: str | None = None
    variant_attributes: dict[str, Any] = {}
    price: dict[str, ProductTemplatePriceInfo] = {}

    @classmethod
    def from_product_product(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            model=ProductTemplate.from_product_template(odoo_rec.product_tmpl_id),
            main=odoo_rec.main,
            name=odoo_rec.full_name or None,
            short_name=odoo_rec.short_name or None,
            variant_count=odoo_rec.product_variant_count,
            categories=[
                ShortProductCategory.from_product_category(shopinvader_category)
                for shopinvader_category in odoo_rec.shopinvader_categ_ids.sorted(
                    "level"
                )
            ],
            sku=odoo_rec.default_code or None,
            variant_attributes=odoo_rec.variant_attributes,
            price=odoo_rec.price,
        )
