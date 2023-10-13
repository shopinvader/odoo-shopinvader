# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas import ProductProduct as BaseProductProduct


class ProductProduct(BaseProductProduct, extends=True):
    short_description: str | None = None
    description: str | None = None

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.short_description = odoo_rec.description_sale_short or None
        obj.description = odoo_rec.description_sale_long or None
        return obj
