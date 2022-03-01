# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import _
from odoo.exceptions import MissingError

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class ShopinvaderAuthJwtServiceContextProvider(Component):
    _name = "auth_jwt.shopinvader.service.context.provider"
    _inherit = "shopinvader.service.context.provider"
    _usage = "shopinvader_auth_jwt_context_provider"

    @property
    def _jwt_payload(self):
        return getattr(self.request, "jwt_payload", None)

    @property
    def _jwt_partner(self):
        partner_id = getattr(self.request, "jwt_partner_id", None)
        if partner_id:
            return self.env["res.partner"].browse(partner_id)

    def _get_shopinvader_partner(self):
        if self._jwt_partner:
            backend = self._get_backend()
            shopinvader_partner = self._jwt_partner._get_invader_partner(backend)
            if not shopinvader_partner:
                raise MissingError(_("The given partner is not bound on the backend"))
            self._validate_partner(backend, shopinvader_partner)
            return shopinvader_partner

        return super()._get_shopinvader_partner()

    def _get_backend(self):
        backend = super(ShopinvaderAuthJwtServiceContextProvider, self)._get_backend()
        if self._jwt_payload:
            audience = self._jwt_payload.get("aud")
            return backend._ensure_jwt_aud(audience)
        return backend
