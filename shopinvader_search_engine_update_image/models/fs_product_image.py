# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class FsProductImage(models.Model):
    _name = "fs.product.image"
    _inherit = ["fs.product.image", "se.product.update.mixin"]

    def _update_se_thumbnails(self):
        for rec in self:
            for thumbnail in rec.image.attachment.se_thumbnail_ids:
                values = thumbnail._prepare_tumbnail(
                    rec.image, thumbnail.size_x, thumbnail.size_y, thumbnail.base_name
                )
                thumbnail.write(values)

    def write(self, vals):
        needs_update = self.needs_product_update(vals)
        res = super().write(vals)
        if needs_update and "specific_image" in vals:
            self._update_se_thumbnails()
        return res

    def get_products(self):
        return self.mapped("product_tmpl_id")
