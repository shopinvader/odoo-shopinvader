# Copyright 2013 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SeIndex(models.Model):

    _inherit = "se.index"

    is_valid = fields.Char(compute="_compute_is_valid")

    @api.depends("lang_id", "model_id")
    @api.depends_context("shopinvader_backend_id")
    def _compute_is_valid(self):
        backend = self.env["shopinvader.backend"]
        backend_id = self.env.context.get("shopinvader_backend_id")
        if backend_id:
            backend = backend.browse(backend_id)
        for rec in self:
            if not rec.lang_id or not backend:
                rec.is_valid = True
                continue
            rec.is_valid = rec.lang_id.id in backend.lang_ids.ids
