# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class Rating(models.Model):
    _inherit = "rating.rating"

    def synchronize_rating(self):
        product_ids = self.filtered(lambda r: r.res_model == "product.product")
        shopinvader_variants = self.env["shopinvader.variant"].search(
            [("record_id", "in", product_ids.mapped("res_id"))]
        )
        shopinvader_variants.synchronize()
