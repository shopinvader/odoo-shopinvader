from odoo import _
from odoo.exceptions import AccessDenied

from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def _decode_token(self, token):
        validator = self.env["auth.jwt.validator"]._get_validator_by_name(
            validator_name="shopinvader"
        )
        while validator:
            try:
                return validator._decode(token)
            except Exception:
                validator = validator.next_validator_id

    def _validator_transfer(self):
        return {
            "token": {"type": "string", "required": True},
        }

    def transfer(self, token=None):
        cart = self._get()
        auth_token = self._decode_token(token)
        if not auth_token or not auth_token.get("email"):
            raise AccessDenied(_("Invalid new auth token"))

        partner = self.env["shopinvader.partner"].search(
            [("partner_email", "=", auth_token["email"])]
        )

        if len(partner) != 1:
            raise AccessDenied(_("Invalid partner email in token"))

        # Change cart partner:
        res_partner_id = partner.record_id.id

        cart.write_with_onchange(
            {
                "partner_id": res_partner_id,
                "partner_shipping_id": res_partner_id,
                "partner_invoice_id": res_partner_id,
            }
        )
        return self._to_json(cart)
