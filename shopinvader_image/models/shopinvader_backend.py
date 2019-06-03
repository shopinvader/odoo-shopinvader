# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    shopinvader_variant_resize_ids = fields.Many2many(
        comodel_name="shopinvader.image.resize",
        relation="product_image_resize",
        string="Product Image Size",
    )
    shopinvader_category_resize_ids = fields.Many2many(
        comodel_name="shopinvader.image.resize",
        relation="category_image_resize",
        string="Category Image Size",
    )
