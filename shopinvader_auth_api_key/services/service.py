# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import AbstractComponent


class BaseShopinvaderService(AbstractComponent):
    _inherit = "base.shopinvader.service"

    def _get_openapi_default_parameters(self):
        defaults = super(BaseShopinvaderService, self)._get_openapi_default_parameters()
        defaults.extend(
            [
                {
                    "name": "API-KEY",
                    "in": "header",
                    "description": "Auth API key "
                    "(Only used when authenticated by API key)",
                    "required": False,
                    "schema": {"type": "string"},
                    "style": "simple",
                },
                {
                    "name": "PARTNER-EMAIL",
                    "in": "header",
                    "description": "Logged partner email "
                    "(Only used when authenticated by API key)",
                    "required": False,
                    "schema": {"type": "string"},
                    "style": "simple",
                },
            ]
        )
        return defaults
