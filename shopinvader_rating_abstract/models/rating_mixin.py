# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class RatingAbstractMixin(models.AbstractModel):
    _inherit = "rating.mixin"
    _name = "shopinvader.rating.mixin.astract"
    _description = "Shopinvader rating mixin"

    @api.depends("index_id", "record_id")
    def _compute_ratings(self):
        for record in self:
            ratings = record.record_id.rating_ids
            record.variant_rating_ids = ratings.filtered(
                lambda r: r.lang_id == record.index_id.lang_id
            )

    def _compute_stats(self):
        self.rating_stats = self._rating_get_repartition(add_stats=True)

    def _rating_domain(self):
        return self.record_id._rating_domain()
