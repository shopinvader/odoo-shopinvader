from odoo import _
from odoo.exceptions import AccessDenied

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

    def search(self):
        cart = self._get(create_if_not_found=False)
        if not cart:
            return {}
        return self._to_json(cart)

    def _get(self, create_if_not_found=True):
        """Get current partner active cart
        We get the cart from the session if it set for backward compatibility

        :return: sale.order recordset (cart)
        """
        domain = [
            ("shopinvader_backend_id", "=", self.shopinvader_backend.id),
            ("typology", "=", "cart"),
            ("state", "=", "draft"),
            ("partner_id", "=", self.partner.id),
        ]

        session_cart_id = self.shopinvader_session.get("cart_id", 0)
        if session_cart_id:
            domain.append(("id", "=", session_cart_id))

        cart = self.env["sale.order"].search(domain, order="date_order desc", limit=1)

        if cart:
            return cart[0]

        if create_if_not_found:
            return self._create_empty_cart()
