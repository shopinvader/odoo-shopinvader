# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderSeasonalConfigLine(models.Model):
    _name = "shopinvader.seasonal.config.line"
    _inherit = ["shopinvader.seasonal.config.line", "se.binding"]
    _se_index_lang_agnostic = True

    index_id = fields.Many2one(compute="_compute_index", store=True, required=False)

    @api.depends(
        "backend_id.se_backend_id",
        "backend_id.se_backend_id.index_ids",
    )
    def _compute_index(self):
        se_backends = self.mapped("backend_id.se_backend_id")
        domain = [
            ("backend_id", "in", se_backends.ids),
            ("model_id.model", "=", self._name),
        ]
        indexes = self.env["se.index"].search(domain)
        for record in self:
            index = indexes.filtered(
                lambda i, r=record: r.backend_id.se_backend_id == i.backend_id
            )
            record.index_id = fields.first(index)

    def _get_shop_data(self):
        """Use pre-computed index data."""
        return self.get_export_data()
