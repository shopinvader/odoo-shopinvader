import logging

from odoo import fields, models

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

            return partner.id
