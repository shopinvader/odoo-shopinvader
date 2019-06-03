# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ShopinvaderVariant(models.Model):
    _name = "shopinvader.variant"
    _inherit = ["shopinvader.variant", "shopinvader.image.mixin"]
    _image_field = "variant_image_ids"
