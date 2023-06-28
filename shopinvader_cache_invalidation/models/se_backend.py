# Copyright 2013 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SeBackend(models.Model):
    _inherit = "se.backend"

    purge_ids = fields.One2many(
        "shopinvader.url.purge", "backend_id", string="Urls to purge"
    )
    purge_nbr = fields.Integer(compute="_compute_purge_nbr", store=True, readonly=True)

    @api.depends("purge_ids")
    def _compute_purge_nbr(self):
        for record in self:
            record.purge_nbr = len(record.purge_ids)
