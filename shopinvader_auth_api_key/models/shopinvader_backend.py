# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models, tools

from odoo.addons.server_environment import serv_config


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    auth_api_key_id = fields.Many2one(
        "auth.api.key",
        "Api Key",
        help="Api_key section used for the authentication of"
        "calls to services dedicated to this backend",
        copy=False,
    )

    _sql_constraints = [
        (
            "auth_api_key_id_uniq",
            "EXCLUDE (auth_api_key_id WITH =) WHERE (auth_api_key_id is not null)",
            _("An authentication API Key can be used by only one backend."),
        )
    ]

    @classmethod
    def _get_api_key_name(cls, auth_api_key):
        for section in serv_config.sections():
            if section.startswith("api_key_") and serv_config.has_option(
                section, "key"
            ):
                if tools.consteq(auth_api_key, serv_config.get(section, "key")):
                    return section
        return None

    @api.model
    @tools.ormcache("self._uid", "auth_api_key_id")
    def _get_id_from_auth_api_key(self, auth_api_key_id):
        return self.search([("auth_api_key_id", "=", auth_api_key_id)]).id

    @api.model
    def _get_from_auth_api_key(self, auth_api_key_id):
        return self.browse(self._get_id_from_auth_api_key(auth_api_key_id))

    def write(self, values):
        if "auth_api_key_id" in values:
            self._get_id_from_auth_api_key.clear_cache(self.env[self._name])
        return super(ShopinvaderBackend, self).write(values)
