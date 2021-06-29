# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import _
from odoo.exceptions import MissingError

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class AuthJwtServiceContextProvider(Component):
    _name = "auth_jwt.shopinvader.service.context.provider"
    _inherit = "shopinvader.service.context.provider"
    _usage = "auth_jwt_component_context_provider"

    @property
    def _jwt_payload(self):
        return getattr(self.request, "jwt_payload", None)

    def _get_shopinvader_partner(self):
        if self._jwt_payload:
            partner_email = self._jwt_payload.get("email")
            backend = self._get_backend()
            if partner_email:
                shopinvader_partner = self._find_partner(backend, partner_email)
                if len(shopinvader_partner) == 1:
                    self._validate_partner(backend, shopinvader_partner)
                    return shopinvader_partner
                else:
                    _logger.warning("Wrong email, jwt payload ignored")
                    if len(shopinvader_partner) > 1:
                        _logger.warning(
                            "More than one shopinvader.partner found for:"
                            " backend_id={} email={}".format(backend.id, partner_email)
                        )
                    # Could be because the email is not related to a partner or
                    # because the partner is inactive
                    raise MissingError(_("The given partner is not found!"))
        return super()._get_shopinvader_partner()

    def _get_backend(self):
        backend = super(AuthJwtServiceContextProvider, self)._get_backend()
        if self._jwt_payload:
            # no jwt_payload = public services...
            audience = self._jwt_payload.get("aud")
            backend_model = self.env["shopinvader.backend"]
            if backend:
                # validate that this backend can be used for the aud
                backend = backend if backend.jwt_aud == audience else backend_model
                if not backend:
                    _logger.warning(
                        "Audience inconsistency for between provided backend and "
                        "jwt toeken: Backend %s (%s != %s)",
                        backend.name,
                        backend.jwt_aud,
                        audience,
                    )
                    return backend
            return backend_model._get_from_jwt_aud(self.request.jwt_payload.get("aud"))
        return backend
