# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class SeBackendAlgolia(models.Model):
    _inherit = "se.backend.algolia"

    # change help msg
    algolia_api_key = fields.Char(
        help="Admin API key with rights to write on indexes"
    )
    algolia_api_key_public = fields.Char(
        string="Public API KEY",
        help="Readonly API key with rights to search only",
    )

    @property
    def _server_env_fields(self):
        env_fields = super()._server_env_fields
        env_fields.update({"algolia_api_key_public": {}})
        return env_fields
