import logging

from odoo import fields, models
from odoo.http import request

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
                # TODO: find a better way
                website_unique_key = request.httprequest.environ.get(
                    "HTTP_WEBSITE_UNIQUE_KEY"
                )
                backend = self.env["shopinvader.backend"]._get_from_website_unique_key(
                    website_unique_key
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
