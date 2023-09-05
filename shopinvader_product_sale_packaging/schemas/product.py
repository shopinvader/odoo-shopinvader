# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas.product import (
    ShopinvaderProduct as BaseShopinvaderProduct,
)


class ShopinvaderProduct(BaseShopinvaderProduct, extends=True):
    sell_only_by_packaging: bool | None = None
    packaging: str | None = None

    @classmethod
    def from_shopinvader_product(cls, odoo_rec):
        obj = super().from_shopinvader_product(odoo_rec)
        obj.sell_only_by_packaging = odoo_rec.sell_only_by_packaging
        obj.packaging = odoo_rec.packaging
        return obj
