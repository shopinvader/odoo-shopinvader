# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.component.core import Component


class ShopinvaderServiceContextProvider(Component):
    _inherit = "shopinvader.service.context.provider"

    def _get_client_header(self):
        res = {}
        headers = self.request.httprequest.environ
        for key, val in headers.items():
            if key.upper().startswith("HTTP_INVADER_CLIENT_"):
                res[key.replace("HTTP_INVADER_CLIENT_", "")] = val
        return res

    def _get_component_context(self):
        res = super(ShopinvaderServiceContextProvider, self)._get_component_context()
        res["client_header"] = self._get_client_header()
        return res
