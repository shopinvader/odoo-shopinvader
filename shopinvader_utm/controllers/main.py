# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.http import request

from odoo.addons.shopinvader.controllers.main import InvaderController


class UtmController(InvaderController):
    @classmethod
    def _get_utm_from_headers(cls, headers):
        utm_params = {
            "campaign": headers.get("HTTP_UTM_CAMPAIGN"),
            "medium": headers.get("HTTP_UTM_MEDIUM"),
            "source": headers.get("HTTP_UTM_SOURCE"),
        }
        return utm_params

    def _get_component_context(self):
        res = super()._get_component_context()
        headers = request.httprequest.environ
        utm_params = self._get_utm_from_headers(headers)
        res["utm"] = utm_params
        return res
