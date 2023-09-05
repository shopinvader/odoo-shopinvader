# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas.category import ShopinvaderCategory


class ProductCategoryShopinvaderSerializer:
    def __init__(self, index):
        self.index = index

    def serialize(self, record):
        return ShopinvaderCategory.from_shopinvader_category(record, index=self.index)
