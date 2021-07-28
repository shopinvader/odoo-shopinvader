# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.addons.component.core import Component

from ..utils import get_partner_work_context


class ShopinvaderServiceContextProvider(Component):
    _name = "shopinvader.service.context.provider"
    _inherit = "base.rest.service.context.provider"
    _collection = "shopinvader.backend"

    def _find_partner(self, backend, partner_email):
        partner_domain = [
            ("partner_email", "=", partner_email),
            ("backend_id", "=", backend.id),
        ]
        return self.env["shopinvader.partner"].search(partner_domain, limit=2)

    def _validate_partner(self, backend, partner):
        return backend._validate_partner(partner)

    def _get_shopinvader_session(self):
        # HTTP_SESS are data that are store in the shopinvader session
        # and forwarded to odoo at each request
        # it allow to access to some specific field of the user session
        # By security always force typing
        # Note: rails cookies store session are serveless ;)
        return {
            "cart_id": int(self.request.httprequest.environ.get("HTTP_SESS_CART_ID", 0))
        }

    def _get_shopinvader_partner(self):
        """Get the partner requesting the api

        At this stage, the partner returned by this method must be the shopinvader
        partner...
        """
        return self.env["shopinvader.partner"].browse()

    def _get_backend(self):
        """Get the requested shopinvader backend instance"""
        website_unique_key = self.request.httprequest.environ.get(
            "HTTP_WEBSITE_UNIQUE_KEY"
        )
        return self.env["shopinvader.backend"]._get_from_website_unique_key(
            website_unique_key
        )

    def _get_component_context(self):
        res = super(ShopinvaderServiceContextProvider, self)._get_component_context()
        res.update(
            {
                "shopinvader_session": self._get_shopinvader_session(),
                "shopinvader_backend": self._get_backend(),
            }
        )
        res.update(get_partner_work_context(self._get_shopinvader_partner()))
        return res
