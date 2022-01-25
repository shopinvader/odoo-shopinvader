from odoo.addons.component.core import Component

import logging

from odoo import _
from odoo.addons.shopinvader_auth_jwt.components.service_context_provider import (
    ShopinvaderAuthJwtServiceContextProvider as ShopinvaderAuthJwtServiceContextProviderParent,
)

_logger = logging.getLogger(__name__)


class ShopinvaderAuthJwtServiceContextProvider(Component):
    _inherit = "auth_jwt.shopinvader.service.context.provider"

    def _get_backend(self):
        # Handle jwt token with several audiences
        if self._jwt_payload:
            # Skip parent
            backend = super(
                ShopinvaderAuthJwtServiceContextProviderParent, self
            )._get_backend()

            # no jwt_payload = public services...
            audience = self._jwt_payload.get("aud")
            if not isinstance(audience, list):
                audience = [audience]

            backend_model = self.env["shopinvader.backend"]
            if backend:
                # validate that this backend can be used for the aud
                backend = backend if backend.jwt_aud in audience else backend_model
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

        return super(ShopinvaderAuthJwtServiceContextProvider, self)._get_backend()
