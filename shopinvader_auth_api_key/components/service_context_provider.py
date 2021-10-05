# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


import logging

from odoo import _
from odoo.exceptions import MissingError

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class ShopinvaderAuthApiKeyServiceContextProvider(Component):
    _name = "auth_api_key.shopinvader.service.context.provider"
    _inherit = "shopinvader.service.context.provider"
    _usage = "shopinvader_auth_api_key_context_provider"

    def _get_shopinvader_partner(self):
        headers = self.request.httprequest.environ
        partner_model = self.env["shopinvader.partner"]
        partner_email = headers.get("HTTP_PARTNER_EMAIL")
        backend = self._get_backend()
        if partner_email:
            partner = self._find_partner(backend, partner_email)
            if len(partner) == 1:
                self._validate_partner(backend, partner)
                return partner
            else:
                _logger.warning("Wrong HTTP_PARTNER_EMAIL, header ignored")
                if len(partner) > 1:
                    _logger.warning(
                        "More than one shopinvader.partner found for:"
                        " backend_id={} email={}".format(backend.id, partner_email)
                    )
                # Could be because the email is not related to a partner or
                # because the partner is inactive
                raise MissingError(_("The given partner is not found!"))
        return partner_model.browse([])

    def _get_backend(self):
        # try to get the backend explicitly requested
        backend = super()._get_backend()
        if not backend:
            # no explicit backend, fallback on the one linKed to the api_key
            auth_api_key_id = getattr(self.request, "auth_api_key_id", None)
            backend = self.env["shopinvader.backend"]._get_from_auth_api_key(
                auth_api_key_id
            )
        return backend
