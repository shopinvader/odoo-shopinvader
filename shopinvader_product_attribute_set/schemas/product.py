# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_product.schemas import ProductProduct as ProductProductBase

from . import ProductAttributeSet


class ProductProduct(ProductProductBase, extends=True):
    attribute_set: ProductAttributeSet | None = None
    attributes: dict[str, str | bool | int] = {}
    structured_attributes: list[dict[str, list | str]] = [{}]

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super(ProductProduct, cls).from_product_product(odoo_rec)
        obj.attribute_set = (
            ProductAttributeSet.from_product_attribute_set(odoo_rec.attribute_set_id)
            if odoo_rec.attribute_set_id
            else None
        )
        obj.attributes = odoo_rec.attributes if odoo_rec.attributes else {}
        obj.structured_attributes = (
            odoo_rec.structured_attributes if odoo_rec.structured_attributes else [{}]
        )
        return obj
