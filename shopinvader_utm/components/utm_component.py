# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.addons.component.core import Component


class UtmComponent(Component):
    _inherit = "shopinvader.service.context.provider"
    _collection = "shopinvader.backend"

    def _get_shopinvader_session(self):
        # HTTP_SESS are data that are store in the shopinvader session
        # and forwarded to odoo at each request
        # it allow to access to some specific field of the user session
        # By security always force typing
        # Note: rails cookies store session are serveless ;)
        res = super()._get_shopinvader_session()
        res.update(
            {
                "campaign": int(
                    self.request.httprequest.environ.get("HTTP_UTM_CAMPAIGN", 0)
                ),
                "medium": int(
                    self.request.httprequest.environ.get("HTTP_UTM_MEDIUM", 0)
                ),
                "source": int(
                    self.request.httprequest.environ.get("HTTP_UTM_SOURCE", 0)
                ),
            }
        )
        return res
