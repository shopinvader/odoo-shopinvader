# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderProduct(models.Model):
    _inherit = "shopinvader.product"
    _order = "sequence, name"

    sequence = fields.Integer(
        help="Determine the display order in the frontend shop",
        default=10,
    )
