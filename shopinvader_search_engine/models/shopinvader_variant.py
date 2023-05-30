# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderVariant(models.Model):
    _inherit = ["shopinvader.variant", "se.binding"]
    _name = "shopinvader.variant"
    _description = "Shopinvader Variant"

    index_id = fields.Many2one(compute="_compute_index", store=True, required=False)

    @api.depends(
        "backend_id.se_backend_id",
        "backend_id.se_backend_id.index_ids",
        "lang_id",
    )
    def _compute_index(self):
        se_backends = self.mapped("backend_id.se_backend_id")
        langs = self.mapped("lang_id")
        domain = [
            ("backend_id", "in", se_backends.ids),
            ("model_id.model", "=", self._name),
            ("lang_id", "in", langs.ids),
        ]
        indexes = self.env["se.index"].search(domain)
        for record in self:
            index = indexes.filtered(
                lambda i, r=record: r.backend_id.se_backend_id == i.backend_id
                and r.lang_id == i.lang_id
            )
            record.index_id = fields.first(index)

    def _get_shop_data(self):
        """Use pre-computed index data."""
        return self.get_export_data()
