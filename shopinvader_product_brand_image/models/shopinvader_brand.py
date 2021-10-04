# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ShopinvaderBrand(models.Model):
    _name = "shopinvader.brand"
    _image_field = "image_ids"

    _inherit = [
        "shopinvader.brand",
        "shopinvader.image.mixin",
    ]
