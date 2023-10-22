import logging
from collections import namedtuple

from odoo import models
from odoo.http import request

from odoo.addons.shopinvader.components.service_context_provider import (
    ShopinvaderServiceContextProvider,
)

_logger = logging.getLogger(__name__)


class AuthJwtValidator(models.Model):
    _inherit = "auth.jwt.validator"

    def _get_shopinvader_backend(self):
        # Remove this hack when shopinvader.partner is no more
        backend = ShopinvaderServiceContextProvider._get_backend(
            namedtuple("DummyWorkContext", ("request", "env"))(
                request=request, env=self.env
            )
        )
        return backend

    def _create_partner_from_payload(self, payload):
        partner = super()._create_partner_from_payload(payload)
        backend = self._get_shopinvader_backend()

        if not backend:
            _logger.debug("No backend found")
            return partner

        self.env["shopinvader.partner"].create(
            {
                "partner_email": partner.email,
                "backend_id": backend.id,
                "record_id": partner.id,
                "external_id": payload.get("sub"),
            }
        )

        return partner

    def _get_partner_from_email(self, email):
        backend = self._get_shopinvader_backend()

        partner = self.env["res.partner"].search(
            [
                ("auth_jwt_email", "=", email),
                ("shopinvader_bind_ids.backend_id", "=", backend.id),
            ]
        )
        if not len(partner):
            partner = self.env["res.partner"].search(
                [
                    ("email", "=", email),
                    ("auth_jwt_email", "=", False),
                    ("shopinvader_bind_ids.backend_id", "=", backend.id),
                ]
            )

        return partner
