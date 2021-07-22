# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderBrand(models.Model):
    _name = "shopinvader.brand"
    _description = "Shopinvader Brand"

    _inherit = [
        "shopinvader.binding",
        "abstract.url",
        "seo.title.mixin",
        "shopinvader.se.binding",
    ]
    _inherits = {"product.brand": "record_id"}
    _order = "sequence"

    record_id = fields.Many2one(
        "product.brand", required=True, ondelete="cascade", index=True
    )
    sequence = fields.Integer()
    meta_description = fields.Char()
    meta_keywords = fields.Char()
    short_description = fields.Html()
    description = fields.Html()
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "record_uniq",
            "unique(backend_id, record_id, lang_id)",
            "A category can only have one binding by backend.",
        )
    ]

    def _compute_automatic_url_key(self):
        self._generic_compute_automatic_url_key()
