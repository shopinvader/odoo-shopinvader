# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated
from uuid import UUID

from fastapi import Depends

from odoo import _, api
from odoo.exceptions import AccessError, MissingError

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from odoo.addons.shopinvader_api_cart.routers import cart_router
from odoo.addons.shopinvader_schema_sale.schemas import Sale


def authenticated_collaborator(
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> ResPartner:
    if partner.unit_profile != "collaborator":
        raise AccessError(_("Only a collaborator can perform this action."))
    return partner


@cart_router.post("/{uuid}/request")
@cart_router.post("/current/request")
@cart_router.post("/request")
async def request(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated["ResPartner", Depends(authenticated_collaborator)],
    uuid: UUID | None = None,
) -> Sale | None:
    cart = env["sale.order"]._find_open_cart(partner.id, str(uuid) if uuid else None)
    if not cart:
        raise MissingError(_("No cart found"))
    cart.action_request_cart()
    return Sale.from_sale_order(cart)
