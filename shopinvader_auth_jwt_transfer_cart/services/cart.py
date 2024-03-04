from odoo import _, fields
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

        old_cart = None
        if self.shopinvader_backend.merge_cart_on_transfer:
            old_partner = self.work.partner
            self.work.partner = partner.record_id
            old_cart = self._get(False)
            self.work.partner = old_partner

        # Change cart partner:
        res_partner_id = partner.record_id.id
        cart.date_order = fields.Datetime.now()
        cart.write_with_onchange(
            {
                "partner_id": res_partner_id,
                "partner_shipping_id": res_partner_id,
                "partner_invoice_id": res_partner_id,
            }
        )

        if old_cart and self.shopinvader_backend.merge_cart_on_transfer:
            # Merge cart:
            for line in old_cart.order_line:
                self._add_item(
                    cart,
                    {
                        "product_id": line.product_id.id,
                        "item_qty": line.product_uom_qty,
                    },
                )

        return self._to_json(cart)
