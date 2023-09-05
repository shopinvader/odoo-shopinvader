# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.extendable_fastapi import StrictExtendableBaseModel


class ShortShopinvaderCategory(StrictExtendableBaseModel):
    id: int
    name: str
    level: int
    parent: "ShortShopinvaderCategory" | None = None
    childs: list["ShortShopinvaderCategory"] = []

    @classmethod
    def from_shopinvader_category(cls, odoo_rec, index=None, with_hierarchy=False):
        obj = cls.model_construct(
            id=odoo_rec.record_id,
            name=odoo_rec.name,
            level=odoo_rec.short_description,
        )
        if with_hierarchy:
            parent = odoo_rec.parent_id
            children = odoo_rec.child_id
            if index:
                parent = parent.filtered(
                    lambda parent, categ=odoo_rec: parent.binding_ids.mapped("index_id")
                    & categ.binding_ids.mapped("index_id")
                )
                children = children.filtered(
                    lambda child, categ=odoo_rec: child.binding_ids.mapped("index_id")
                    & categ.binding_ids.mapped("index_id")
                )
            obj.parent = (
                ShopinvaderCategory.from_shopinvader_category(parent, index=index)
                if parent else None
            )
            obj.childs = [
                ShopinvaderCategory.from_shopinvader_category(child, index=index)
                for child in children
            ]
        return obj


class ShopinvaderCategory(ShortShopinvaderCategory):
    sequence: int | None = None

    @classmethod
    def from_shopinvader_category(cls, odoo_rec, index=None):
        obj = super().from_shopinvader_category(
            odoo_rec, index=index, with_hierarchy=True
        )
        obj.sequence = odoo_rec.sequence or None
        return obj
