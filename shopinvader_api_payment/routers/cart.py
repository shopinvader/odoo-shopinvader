# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


import hashlib
import hmac

from odoo.addons.shopinvader_api_cart.routers.cart import cart_router


@cart_router.get("/get_payment_form", status_code=200)
@cart_router.get("/{uuid}/get_payment_form", status_code=200)
def get_payment_form(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated["ResPartner", Depends(authenticated_partner)],
    uuid: Optional[str] = None,
):
    cart = env["sale.order"].sudo().search([("uuid", "=", uuid)])
    # cart = env["sale.order"]._find_open_cart(partner.id, uuid)
    return {"form": env["shopinvader_api_cart.service.helper"].sudo().pay(cart)}
    # return CartResponse.from_cart(cart) if cart else {}


class ShopinvaderApiCartServiceHelper(models.AbstractModel):
    _inherit = "shopinvader_api_cart.service.helper"

    def pay(self, cart):
        acquirer_id = 16  # 7 #17
        acquirer = self.env["payment.acquirer"].browse(acquirer_id)
        order_id = cart.id
        invoice_id = None
        currency_id = cart.currency_id.id or 1
        partner_id = cart.partner_id.id
        reference_values = order_id and {"sale_order_ids": [(4, order_id)]} or {}
        reference = cart.name
        reference = self.env["payment.transaction"]._compute_reference(
            values=reference_values, prefix=reference
        )
        amount = cart.amount_total
        amount = cart.amount_total

        values = {
            "acquirer_id": int(acquirer_id),
            "reference": reference,
            "amount": float(amount),
            "currency_id": int(currency_id),
            "partner_id": partner_id,
            "type": "form_save"
            if acquirer.save_token != "none" and partner_id
            else "form",
        }

        if order_id:
            values["sale_order_ids"] = [(6, 0, [order_id])]
        elif invoice_id:
            values["invoice_ids"] = [(6, 0, [invoice_id])]

        reference_values = order_id and {"sale_order_ids": [(4, order_id)]} or {}
        reference_values.update(acquirer_id=int(acquirer_id))
        values["reference"] = self.env["payment.transaction"]._compute_reference(
            values=reference_values, prefix=reference
        )
        tx = (
            self.env["payment.transaction"]
            .sudo()
            .with_context(lang=None)
            .create(values)
        )
        secret = self.env["ir.config_parameter"].sudo().get_param("database.secret")
        token_str = "%s%s%s" % (
            tx.id,
            tx.reference,
            float_repr(tx.amount, precision_digits=tx.currency_id.decimal_places),
        )
        token = hmac.new(
            secret.encode("utf-8"), token_str.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        tx.return_url = "/website_payment/confirm?tx_id=%d&access_token=%s" % (
            tx.id,
            token,
        )

        # session hack
        # PaymentProcessing.add_payment_transaction(tx)

        render_values = {
            "partner_id": partner_id,
            "type": tx.type,
        }

        return acquirer.sudo().render(
            tx.reference, float(amount), int(currency_id), values=render_values
        )
