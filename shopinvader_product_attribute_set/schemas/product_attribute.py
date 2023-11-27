# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from __future__ import annotations

from enum import Enum

from extendable_pydantic import StrictExtendableBaseModel

from odoo.addons.product.models.product_product import ProductProduct

from ..models.attribute_attribute import AttributeAttribute


class ProductAttributeType(Enum):
    """Enum for product attribute type"""

    char = "char"
    text = "text"
    select = "select"
    multiselect = "multiselect"
    boolean = "boolean"
    integer = "integer"
    date = "date"
    datetime = "datetime"
    binary = "binary"


class ProductAttribute(StrictExtendableBaseModel):
    name: str
    key: str
    value: str | bool | int | list[str]
    type: ProductAttributeType

    @classmethod
    def _get_value_for_attribute(
        cls,
        product: ProductProduct,
        attr: AttributeAttribute,
        string_mode: bool = False,
    ) -> str | bool | int | list[str]:
        if attr.attribute_type == "select":
            return product[attr.name].display_name or ""
        elif attr.attribute_type == "multiselect":
            return product[attr.name].mapped("display_name")
        elif string_mode and attr.attribute_type == "boolean":
            return product[attr.name] and "true" or "false"
        elif string_mode or attr.attribute_type in ("char", "text"):
            return "%s" % (product[attr.name] or "")
        else:
            return product[attr.name] or ""

    @classmethod
    def from_product_attribute(
        cls, product: ProductProduct, attribute: AttributeAttribute
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        return cls.model_construct(
            name=attribute.field_description,
            key=attribute.export_name,
            value=cls._get_value_for_attribute(product, attribute, string_mode=True),
            type=ProductAttributeType(attribute.attribute_type),
        )
