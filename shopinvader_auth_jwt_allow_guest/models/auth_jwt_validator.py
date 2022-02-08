from collections import namedtuple
import logging

from odoo import fields, models
from odoo.http import request
from odoo.addons.shopinvader.components.service_context_provider import (
    ShopinvaderServiceContextProvider,
)

_logger = logging.getLogger(__name__)


class AuthJwtValidator(models.Model):
    _inherit = "auth.jwt.validator"

    partner_id_strategy = fields.Selection(
        selection_add=[("email_create", "From email claim, create if not found")]
    )

    def _get_partner_id(self, payload):
        if self.partner_id_strategy == "email_create":
            email = payload.get("email")
            if not email:
                _logger.debug("JWT payload does not have an email claim")
                return
            partner = self.env["res.partner"].search([("email", "=", email)])
            if not len(partner):
                partner = self.env["res.partner"].create(
                    {"name": "Guest", "email": email}
                )

                # TODO: The dummy call to the context provider is not ideal
                backend = ShopinvaderServiceContextProvider._get_backend(
                    namedtuple("DummyWorkContext", ("request", "env"))(
                        request=request, env=self.env
                    )
                )

                self.env["shopinvader.partner"].create(
                    {
                        "partner_email": email,
                        "backend_id": backend.id,
                        "is_guest": True,
                        "record_id": partner.id,
                        "external_id": payload.get("sub"),
                    }
                )

            return partner.id
        return super()._get_partner_id(payload)
