# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from extendable_pydantic.models import StrictExtendableBaseModel

from odoo.addons.shopinvader_product.schemas import ShortProductCategory


class HierarchicalCategory(StrictExtendableBaseModel):
    level: int
    value: str
    order: int = 0
    ancestors: list[str] = []

    @classmethod
    def from_product_category(cls, odoo_rec):
        parent_names = []
        parent_id = ShortProductCategory._get_parent(odoo_rec)
        while parent_id:
            parent_names.append(parent_id.name)
            parent_id = ShortProductCategory._get_parent(parent_id)
        return cls.model_construct(
            level=odoo_rec.level + 1,
            value=odoo_rec.name,
            ancestors=parent_names,
            order=odoo_rec.sequence,
        )
