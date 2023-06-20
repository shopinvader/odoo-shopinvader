# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import APIRouter, Depends

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import authenticated_partner_env

from ..schemas import CartResponse, CartSyncInput

cart_router = APIRouter()


@cart_router.get("/", response_model=CartResponse | dict)
@cart_router.get("/{uuid}", response_model=CartResponse | dict)
def get(
    env: Annotated[Environment, Depends(authenticated_partner_env)],
    uuid: str | None = None,
) -> CartResponse:
    """
    Return an empty dict if no cart was found
    """
    cart = env["sale.order"]._find_open_cart(uuid)
    return CartResponse.from_orm(cart) if cart else {}


@cart_router.post("/sync", response_model=CartResponse | dict, status_code=201)
@cart_router.post("/sync/{uuid}", response_model=CartResponse | dict, status_code=201)
def sync(
    data: CartSyncInput,
    env: Annotated[Environment, Depends(authenticated_partner_env)],
    uuid: str | None = None,
) -> CartResponse:
    cart = env["sale.order"]._sync_cart(uuid, data.transactions)
    return CartResponse.from_orm(cart) if cart else {}
