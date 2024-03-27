# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplateLink(models.Model):
    _name = "product.template.link"
    _inherit = ["product.template.link", "se.product.update.mixin"]

    def get_products(self):
        lefts = self.mapped("left_product_tmpl_id")
        rights = self.mapped("right_product_tmpl_id")
        return lefts | rights
