# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class FsProductBrandImage(models.Model):
    _inherit = "fs.product.brand.image"

    def get_brands(self):
        return self.mapped("brand_id")

    @api.model_create_multi
    def create(self, vals_list):
        res = super(FsProductBrandImage, self).create(vals_list)
        res.get_brands().shopinvader_mark_to_update()
        return res

    def write(self, vals):
        needs_update = self.needs_brand_update(vals)
        if needs_update:
            products = self.get_brands()
        res = super(FsProductBrandImage, self).write(vals)
        if needs_update:
            (products | self.get_brands()).shopinvader_mark_to_update()
        return res

    def unlink(self):
        products = self.get_brands()
        res = super(FsProductBrandImage, self).unlink()
        products.shopinvader_mark_to_update()
        return res

    def needs_brand_update(self, vals):
        return True
