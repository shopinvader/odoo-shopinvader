# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = ["product.category", "seo.title.mixin"]

    meta_description = fields.Char()
    meta_keywords = fields.Char()
