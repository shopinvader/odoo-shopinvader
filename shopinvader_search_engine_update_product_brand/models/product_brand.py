# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductBrand(models.Model):
    _inherit = "product.brand"

    def write(self, vals):
        res = super(ProductBrand, self).write(vals)
        self.shopinvader_mark_to_update()
        return res

    def shopinvader_mark_to_update(self):
        res = super(ProductBrand, self).shopinvader_mark_to_update()
        self._shopinvader_mark_to_update_associated_products()
        return res

    def _shopinvader_mark_to_update_associated_products(self):
        self.product_ids.shopinvader_mark_to_update()
