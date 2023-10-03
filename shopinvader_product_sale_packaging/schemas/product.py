# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas import ProductProduct as BaseProductProduct

from . import ProductPackaging


class ProductProduct(BaseProductProduct, extends=True):
    sell_only_by_packaging: bool | None = None
    packaging: list[ProductPackaging] = []

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.sell_only_by_packaging = odoo_rec.sell_only_by_packaging
        context = {"_packaging_filter": lambda x: x.shopinvader_display}
        packaging = odoo_rec.with_context(**context)._ordered_packaging()
        packaging_contained_mapping = odoo_rec.with_context(
            **context
        ).packaging_contained_mapping
        obj.packaging = [
            ProductPackaging.from_packaging(
                odoo_product=odoo_rec,
                packaging=pkg,
                packaging_contained_mapping=packaging_contained_mapping,
            )
            for pkg in packaging
        ]

        return obj
