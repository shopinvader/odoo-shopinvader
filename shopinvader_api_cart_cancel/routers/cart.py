# Copyright 2025 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response

from odoo.addons.shopinvader_api_cart.routers.cart import CartHelper, cart_helper

cart_cancel_router = APIRouter(tags=["carts"])


@cart_cancel_router.post("/cancel/{uuid}")
@cart_cancel_router.post("/cancel/current")
def cancel_cart(
    helper: Annotated[CartHelper, Depends(cart_helper)],
    uuid: UUID | None = None,
):
    """Cancel cart.

    You can use this endpoint to cancel current cart or a specific cart
    """
    cart = helper._get_cart(uuid)
    if not cart:
        return Response(status_code=404)
    else:
        cart.action_cancel()
        return Response(status_code=200)
