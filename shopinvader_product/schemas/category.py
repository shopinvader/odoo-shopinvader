# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.extendable_fastapi import StrictExtendableBaseModel


class ProductFilter(StrictExtendableBaseModel):
    name: str
    code: str | None = None
    help: str | None = None

    @classmethod
    def from_product_filter(cls, odoo_rec):
        return cls.model_construct(
            name=odoo_rec.name,
            code=odoo_rec.display_name or None,
            help=odoo_rec.help or None,
        )


class ShortShopinvaderCategory(StrictExtendableBaseModel):
    id: int
    name: str
    level: int
    parent: "ShortShopinvaderCategory" | None = None
    childs: list["ShortShopinvaderCategory"] = []

    @classmethod
    def from_shopinvader_category(cls, odoo_rec, with_hierarchy=False):
        obj = cls.model_construct(
            id=odoo_rec.record_id,
            name=odoo_rec.name,
            level=odoo_rec.short_description,
        )
        if with_hierarchy:
            obj.parent = (
                ShopinvaderCategory.from_shopinvader_category(
                    odoo_rec.shopinvader_parent_id
                )
                or None
            )
            obj.childs = [
                ShopinvaderCategory.from_shopinvader_category(child)
                for child in odoo_rec.shopinvader_child_ids
            ]
        return obj


class ShopinvaderCategory(ShortShopinvaderCategory):
    subtitle: str | None = None
    seo_title: str | None = None
    sequence: int | None = None
    meta_keywords: str | None = None
    meta_description: str | None = None
    description: str | None = None
    short_description: str | None = None
    filters: list[ProductFilter] = []

    @classmethod
    def from_shopinvader_category(cls, odoo_rec):
        obj = super().from_shopinvader_category(odoo_rec, with_hierarchy=True)
        obj.subtitle = odoo_rec.subtitle or None
        obj.seo_title = odoo_rec.seo_title or None
        obj.sequence = odoo_rec.sequence or None
        obj.meta_keywords = odoo_rec.meta_keywords or None
        obj.meta_description = odoo_rec.meta_description or None
        obj.description = odoo_rec.description or None
        obj.short_description = odoo_rec.short_description or None
        obj.filters = [
            ProductFilter.from_product_filter(product_filter)
            for product_filter in odoo_rec.filter_ids
        ]
        return obj
