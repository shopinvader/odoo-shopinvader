# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        self.mapped("product_variant_ids").shopinvader_mark_to_update()
        return res

    def shopinvader_mark_to_update(self):
        self.mapped("product_variant_ids").shopinvader_mark_to_update()
