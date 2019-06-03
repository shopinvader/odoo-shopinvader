# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderImageResize(models.Model):
    _name = "shopinvader.image.resize"
    _description = "Shopinvader Image Resize"

    name = fields.Char(required=True)
    key = fields.Char(required=True)
    size_x = fields.Integer(required=True)
    size_y = fields.Integer(required=True)

    @api.depends("size_x", "size_y")
    def _compute_display_name(self):
        for record in self:
            record.display_name = "{} ({}x{})".format(
                record.name, record.size_x, record.size_y
            )
