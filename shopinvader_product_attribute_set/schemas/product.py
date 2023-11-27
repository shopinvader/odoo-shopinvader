# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from __future__ import annotations

from odoo.addons.product.models import product_product
from odoo.addons.shopinvader_product.schemas import product

from . import ProductAttributeSet
from .product_attribute import ProductAttribute
from .product_attribute_group import ProductAttributeGroup


class ProductProduct(product.ProductProduct, extends=True):
    attribute_set: ProductAttributeSet | None = None
    attributes: dict[str, str | bool | int | list[str]] = {}
    structured_attributes: list[ProductAttributeGroup] = []

    @classmethod
    def from_product_product(
        cls, odoo_rec: product_product.ProductProduct
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        obj = super().from_product_product(odoo_rec)
        obj.attribute_set = (
            ProductAttributeSet.from_product_attribute_set(odoo_rec.attribute_set_id)
            if odoo_rec.attribute_set_id
            else None
        )
        obj.attributes = cls._compute_attributes(odoo_rec)
        obj.structured_attributes = cls._compute_structured_attributes(odoo_rec)
        return obj

    @classmethod
    def _compute_attributes(
        cls, record: product_product.ProductProduct
    ) -> dict[str, str | bool | int | list[str]]:
        attributes = {}
        for attr in record.attribute_set_id.attribute_ids:
            # all attr start with "x_" we remove it for the export
            attributes[attr.export_name] = ProductAttribute._get_value_for_attribute(
                record, attr, string_mode=False
            )
        return attributes

    @classmethod
    def _compute_structured_attributes(
        cls, record: product_product.ProductProduct
    ) -> list[ProductAttributeGroup]:
        strc_attr = {}
        attr_set = record.attribute_set_id
        groups = attr_set.attribute_ids.mapped("attribute_group_id")
        for group in groups:
            strc_attr[group.id] = ProductAttributeGroup.model_construct(
                group_name=group.name, fields=[]
            )

        for attr in attr_set.attribute_ids:
            strc_attr[attr.attribute_group_id.id].fields.append(
                ProductAttribute.from_product_attribute(record, attr)
            )
        return strc_attr.values()
