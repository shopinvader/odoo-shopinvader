# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel


class ProductAttributeSet(StrictExtendableBaseModel):
    id: int
    name: str

    @classmethod
    def from_product_attribute_set(cls, odoo_rec):
        return cls.model_construct(id=odoo_rec.id, name=odoo_rec.name)
