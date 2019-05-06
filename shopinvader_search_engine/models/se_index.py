# -*- coding: utf-8 -*-
# Copyright 2013 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SeIndex(models.Model):

    _inherit = "se.index"

    is_valid = fields.Char(compute="_compute_is_valid")

    @api.depends("lang_id", "model_id")
    def _compute_is_valid(self):
        for rec in self:
            active_id = self.env.context.get("shopinvader_backend_id")
            active_id = self.env["shopinvader.backend"].browse(active_id)
            if active_id and rec.lang_id in active_id.lang_ids:
                rec.is_valid = True
