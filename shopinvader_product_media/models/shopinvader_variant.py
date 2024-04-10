# Copyright 2024 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    variant_media_ids = fields.Many2many(
        "product.media.relation",
        compute="_compute_variant_media_ids",
    )

    @api.depends(
        "record_id.variant_media_ids.media_id.active",
    )
    def _compute_variant_media_ids(self):
        for variant in self:
            variant.variant_media_ids = (
                variant.record_id.variant_media_ids.media_id.filtered("active")
            )
