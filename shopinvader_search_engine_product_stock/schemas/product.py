# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Any

from odoo.addons.shopinvader_product.schemas import ProductProduct as BaseProduct


class ProductProduct(BaseProduct, extends=True):
    stock: dict[str, Any] = {}

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.stock = odoo_rec.stock_data if odoo_rec.stock_data else {}
        return obj
