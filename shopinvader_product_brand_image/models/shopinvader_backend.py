# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderBackend(models.Model):

    _inherit = "shopinvader.backend"

    shopinvader_brand_resize_ids = fields.Many2many(
        comodel_name="shopinvader.image.resize",
        relation="brand_image_resize",
        string="Brand Image Size",
    )
