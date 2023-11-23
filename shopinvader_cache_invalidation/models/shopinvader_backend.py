# Copyright 2023 Akretion (https://www.akretion.com).
# @author Matthieu SAISON <matthieu.saison@akretion.com>
# License AGPL-3.0 or later (https: //www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    purge_ids = fields.One2many(
        "shopinvader.url.purge", "backend_id", string="Urls to purge"
    )
    purge_nbr = fields.Integer(compute="_compute_purge_nbr", store=True, readonly=True)

    cache_refresh_secret = fields.Char()

    @property
    def _server_env_fields(self):
        env_fields = super()._server_env_fields
        env_fields.update({"cache_refresh_secret": {}})
        return env_fields

    @api.depends("purge_ids")
    def _compute_purge_nbr(self):
        for record in self:
            record.purge_nbr = len(record.purge_ids)
