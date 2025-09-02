# Copyright 2025 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response

from odoo import api

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)

cart_cancel_router = APIRouter(tags=["carts"])


@cart_cancel_router.post("/cancel/{uuid}")
@cart_cancel_router.post("/cancel/current")
def cancel_cart(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated["ResPartner", Depends(authenticated_partner)],
    uuid: UUID | None = None,
):
    """Cancel cart.

    You can use this endpoint to cancel current cart or a specific cart
    """
    cart = env["sale.order"]._find_open_cart(partner.id, str(uuid) if uuid else None)
    if not cart:
        return Response(status_code=404)
    else:
        cart.action_cancel()
        return Response(status_code=200)
