# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductBrand(models.Model):
    _name = "product.brand"
    _inherit = ["product.brand", "seo.title.mixin", "abstract.url"]

    active = fields.Boolean(default=True)
    sequence = fields.Integer()
    meta_description = fields.Char()
    meta_keywords = fields.Char()
    short_description = fields.Text()
