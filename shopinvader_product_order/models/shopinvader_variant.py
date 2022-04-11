# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"
    _order = "sequence, name"

    sequence = fields.Integer(
        related="shopinvader_product_id.sequence",
        store=True,
    )
