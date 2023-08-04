# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas.product import ShopinvaderVariant


class ProductProductShopinvaderSerializer:
    def serialize(self, record):
        return ShopinvaderVariant.from_shopinvader_variant(record)
