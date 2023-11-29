# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from odoo import api, fields, models

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.delivery.models.delivery_carrier import DeliveryCarrier
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)

from ..schemas import (
    DeliveryCarrier as DeliveryCarrierSchema,
    DeliveryCarrierSearch,
    DeliveryCarrierWithPrice,
)

delivery_carrier_router = APIRouter(tags=["delivery_carriers"])


@delivery_carrier_router.get("/delivery_carriers")
def search(
    data: Annotated[DeliveryCarrierSearch, Depends()],
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> list[DeliveryCarrierSchema]:
    """
    Returns the list of all available carriers.

    The field type is a technical field only use inform if the carrier
    provides some specialized functionalities
    """
    delivery_carriers = (
        env["shopinvader_api_delivery_carrier.delivery_carrier_router.helper"]
        .new({"partner": partner})
        ._search(data, cart=None)
    )
    return [
        DeliveryCarrierSchema.from_delivery_carrier(delivery_carrier)
        for delivery_carrier in delivery_carriers
    ]


@delivery_carrier_router.get("/{uuid}/delivery_carriers")
@delivery_carrier_router.get("/current/delivery_carriers")
def search_current(
    data: Annotated[DeliveryCarrierSearch, Depends()],
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    uuid: UUID | None = None,
) -> list[DeliveryCarrierWithPrice]:
    """
    Returns the list of available carriers

    The list will be limited to the carriers applying to the current cart
    and a price will be filled into the response.

    The field type is a technical field only use inform if the carrier
    provides some specialized functionalities
    """
    cart = env["sale.order"]._find_open_cart(partner.id, str(uuid) if uuid else None)
    if not cart:
        raise HTTPException(status_code=404)

    delivery_carriers = (
        env["shopinvader_api_delivery_carrier.delivery_carrier_router.helper"]
        .new({"partner": partner})
        ._search(data, cart=cart)
    )
    return [
        DeliveryCarrierWithPrice.from_delivery_carrier(delivery_carrier, cart=cart)
        for delivery_carrier in delivery_carriers
    ]


class ShopinvaderApiDeliveryRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_delivery_carrier.delivery_carrier_router.helper"
    _description = "ShopInvader API Delivery Carrier Router Helper"

    partner = fields.Many2one("res.partner")

    @api.model
    def _available_carriers(self, cart):
        cart.ensure_one()
        sort_key = {}
        available_carriers = cart.shopinvader_available_carrier_ids.browse()
        for carrier in cart.shopinvader_available_carrier_ids:
            result = carrier.rate_shipment(cart)
            if result.get("success"):
                available_carriers |= carrier
                sort_key.update({carrier: result.get("price", 0.0)})
        # Sort on the price
        return available_carriers.sorted(lambda c: sort_key.get(c))

    def _search(self, params, cart=None) -> DeliveryCarrier:
        """
        NB: paging is not supported here, because of the complex
        _available_carriers method and the sorted implemented inside
        """
        if cart:
            if params.country_id or params.zipcode:
                ctx = self.env.context.copy()
                ctx.update(
                    {
                        "delivery_force_country_id": params.country_id or 0,
                        "delivery_force_zip_code": params.zipcode or "",
                    }
                )
                cart = cart.with_context(**ctx)
            delivery_carriers = self._available_carriers(cart)
            return delivery_carriers
        return self.env["delivery.carrier"].search([])
