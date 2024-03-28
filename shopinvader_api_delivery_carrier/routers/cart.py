# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import Depends

from odoo import _, api, models
from odoo.exceptions import UserError

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from odoo.addons.sale.models.sale_order import SaleOrder
from odoo.addons.shopinvader_api_cart.routers import cart_router
from odoo.addons.shopinvader_api_cart.schemas import CartTransaction
from odoo.addons.shopinvader_schema_sale.schemas import Sale

from ..schemas import DeliveryCarrierInput


@cart_router.post("/set_carrier")
@cart_router.post("/{uuid}/set_carrier")
@cart_router.post("/current/set_carrier")
def set_carrier(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated["ResPartner", Depends(authenticated_partner)],
    data: DeliveryCarrierInput,
    uuid: str | None = None,
) -> Sale | None:
    """
    If cart is found, set the carrier on it.
    """
    cart = env["sale.order"]._find_open_cart(partner.id, uuid)
    if not cart:
        raise UserError(_("There is no cart"))
    env["shopinvader_api_cart.cart_router.helper"]._set_carrier(cart, data)
    return Sale.from_sale_order(cart) if cart else None


class ShopinvaderApiCartRouterHelper(models.AbstractModel):
    _inherit = "shopinvader_api_cart.cart_router.helper"

    # Set carrier
    @api.model
    def _set_carrier_and_price(self, cart, carrier_id):
        ctx = self.env.context.copy()
        ctx.update({"default_order_id": cart.id, "default_carrier_id": carrier_id})
        wizard = self.env["choose.delivery.carrier"].with_context(**ctx).create({})
        wizard._onchange_carrier_id()
        wizard.button_confirm()
        return wizard.delivery_price

    @api.model
    def _set_carrier(self, cart, data):
        """
        Check if the carrier is available and set it on the cart.
        """
        carrier_id = data.carrier_id
        if carrier_id not in cart.shopinvader_available_carrier_ids.ids:
            raise UserError(_("This delivery method is not available for your order"))
        self._set_carrier_and_price(cart, carrier_id)

    # Improve cart synchronization: remove carrier everytime an item is updated
    @api.model
    def _sync_cart(
        self,
        partner: ResPartner,
        cart: SaleOrder,
        uuid: str,
        transactions: list[CartTransaction],
    ):
        cart = super()._sync_cart(partner, cart, uuid, transactions)
        if transactions:
            cart._remove_delivery_line()
        return cart
