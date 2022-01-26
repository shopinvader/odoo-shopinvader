from odoo.exceptions import AccessDenied
from odoo import _

from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def _validator_transfert(self):
        return {
            "token": {"type": "string", "required": True},
        }

    def _decode_token(self, token):
        for jwt_validator in self.env["auth.jwt.validator"].search([]):
            try:
                return jwt_validator._decode(token)
            except Exception:
                continue

    def transfert(self, token=None):
        cart = self._get()
        auth_token = self._decode_token(token)
        if not auth_token or not auth_token.get("email"):
            raise AccessDenied(_("Invalid new auth token"))

        partner = self.env["shopinvader.partner"].search(
            [("partner_email", "=", auth_token["email"])]
        )

        if len(partner) != 1:
            raise AccessDenied(_("Invalid partner email in token"))

        cart.partner_id = partner.record_id
        return self._to_json(cart)
