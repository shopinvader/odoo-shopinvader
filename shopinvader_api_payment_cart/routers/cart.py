# Copyright 2024 ACSONE SA (https://acsone.eu).
# @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException

from odoo import api

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from odoo.addons.payment import utils as payment_utils
from odoo.addons.shopinvader_api_cart.routers import cart_router
from odoo.addons.shopinvader_api_payment.routers.utils import Payable
from odoo.addons.shopinvader_api_payment.schemas import PaymentData


@cart_router.get("/{uuid}/payable")
@cart_router.get("/current/payable")
def init(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated["ResPartner", Depends(authenticated_partner)],
    uuid: UUID | None = None,
) -> PaymentData | None:
    """Prepare payment data for the current cart.

    This route is authenticated, so we can verify the cart
    is accessible by the authenticated partner.
    """
    cart = env["sale.order"]._find_open_cart(partner.id, str(uuid) if uuid else None)
    if not cart:
        raise HTTPException(status_code=404)
    sale_order = env["sale.order"].browse(cart.id)
    payment_data = {
        "payable": Payable(
            payable_id=cart.id,
            payable_model="sale.order",
            payable_reference=sale_order.name,
            amount=sale_order.amount_total,
            amount_formatted=sale_order.currency_id.format(sale_order.amount_total),
            currency_id=sale_order.currency_id.id,
            partner_id=sale_order.partner_id.id,
            company_id=sale_order.company_id.id,
        ).model_dump_json(),
        "payable_reference": sale_order.name,
        "amount": sale_order.amount_total,
        "amount_formatted": sale_order.currency_id.format(sale_order.amount_total),
        "currency_code": sale_order.currency_id.name,
    }
    payment_data["access_token"] = payment_utils.generate_access_token(
        payment_data["payable"]
    )
    return PaymentData(**payment_data)
