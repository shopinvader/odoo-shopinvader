# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel

from .product_attribute import ProductAttribute


class ProductAttributeGroup(StrictExtendableBaseModel):
    group_name: str
    fields: list[ProductAttribute]
