# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ShopinvaderVariant(models.Model):
    _inherit = ["shopinvader.variant", "shopinvader.rating.mixin.astract"]
    _name = "shopinvader.variant"

    variant_rating_ids = fields.One2many(
        comodel_name="rating.rating",
        compute="_compute_ratings",
        string="Shopinvader Ratings",
    )
    rating_stats = fields.Serialized(
        compute="_compute_stats", string="Ratings Statistics"
    )
