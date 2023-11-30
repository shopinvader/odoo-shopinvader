# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Annotated

from pydantic import Field

from odoo.addons.shopinvader_product.schemas import ProductProduct as BaseProductProduct

from . import HierarchicalCategory


class ProductProduct(BaseProductProduct, extends=True):
    hierarchicalCategories: Annotated[
        list[HierarchicalCategory],
        Field(serialization_alias="hierarchicalCategories"),
    ] = []

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        for shopinvader_category in odoo_rec.shopinvader_categ_ids.sorted("level"):
            obj.hierarchicalCategories.append(
                HierarchicalCategory.from_product_category(shopinvader_category)
            )
        return obj
