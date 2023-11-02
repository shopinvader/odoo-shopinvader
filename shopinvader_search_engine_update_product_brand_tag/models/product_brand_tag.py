# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductBrandTag(models.Model):
    _inherit = "product.brand.tag"

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ProductBrandTag, self).create(vals_list)
        res.product_brand_ids.shopinvader_mark_to_update()
        return res

    def write(self, vals):
        res = super(ProductBrandTag, self).write(vals)
        if "name" in vals or "product_brand_ids" in vals:
            self.product_brand_ids.shopinvader_mark_to_update()
        return res

    def unlink(self):
        self.product_brand_ids.shopinvader_mark_to_update()
        return super(ProductBrandTag, self).unlink()
