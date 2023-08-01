# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from __future__ import annotations

from extendable_pydantic import StrictExtendableBaseModel


class ShortProductCategory(StrictExtendableBaseModel):
    id: int
    name: str
    level: int
    parent: ShortProductCategory | None = None
    childs: list[ShortProductCategory] = []

    @classmethod
    def _get_parent(cls, odoo_rec):
        return odoo_rec.parent_id

    @classmethod
    def _get_children(cls, odoo_rec):
        return odoo_rec.child_id

    @classmethod
    def from_product_category(cls, odoo_rec, with_parent=False, with_child=False):
        obj = cls.model_construct(
            id=odoo_rec.id, name=odoo_rec.name, level=odoo_rec.level
        )
        if with_parent:
            parent = cls._get_parent(odoo_rec)
            obj.parent = (
                ShortProductCategory.from_product_category(parent, with_parent=True)
                if parent
                else None
            )
        if with_child:
            children = cls._get_children(odoo_rec)
            obj.childs = [
                ShortProductCategory.from_product_category(child, with_child=True)
                for child in children
            ]
        return obj


class ProductCategory(ShortProductCategory):
    sequence: int | None = None

    @classmethod
    def from_product_category(cls, odoo_rec):
        obj = super().from_product_category(odoo_rec, with_parent=True, with_child=True)
        obj.sequence = odoo_rec.sequence or None
        return obj
