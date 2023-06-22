from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import api, models
from odoo.api import Environment

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from odoo.addons.fastapi.schemas import PagedCollection
from odoo.addons.shopinvader_schema_address.schemas import (
    BillingAddress,
    ShippingAddress,
)

from ..schemas import AddressCreate, AddressUpdate

# create a router
address_router = APIRouter(tags=["addresses"])

# --- Billing addresses ---


@address_router.get("/addresses/billing", response_model=BillingAddress)
def get_billing_address(
    partner:Annotated[ResPartner, Depends(authenticated_partner)],
) -> BillingAddress:
    """
    Get billing address of authenticated user
    billing address corresponds to authenticated partner
    """
    address = partner._get_shopinvader_billing_address()
    return BillingAddress.from_res_partner(address)


@address_router.post(
    "/addresses/billing", response_model=BillingAddress, status_code=201
)
def update_billing_address(
    data: AddressUpdate,
    partner:Annotated[ResPartner, Depends(authenticated_partner)],
) -> BillingAddress:
    """
    Update billing address of authenticated user
    billing address corresponds to authenticated partner
    """
    vals = data.to_res_partner_vals()
    address = partner._update_shopinvader_billing_address(vals)
    return BillingAddress.from_res_partner(address)


# --- Shipping address ---


@address_router.get(
    "/addresses/shipping", response_model=PagedCollection[ShippingAddress]
)
@address_router.get(
    "/addresses/shipping/{_id}", response_model=PagedCollection[ShippingAddress]
)
def get_shipping_address(
    partner:Annotated[ResPartner, Depends(authenticated_partner)],
    _id: int | None = None,
) -> PagedCollection[ShippingAddress]:
    """
    Get shipping addresses of authenticated user
    Can be used to get every shipping address: /addresses/shipping
    Can be used to get one specific address: /addresses/shipping/_id
    """
    addresses = partner._get_shopinvader_shipping_addresses(_id)
    return PagedCollection[ShippingAddress](
        total=len(addresses),
        items=[ShippingAddress.from_res_partner(rec) for rec in addresses],
    )


@address_router.post(
    "/addresses/shipping", response_model=ShippingAddress, status_code=201
)
@address_router.post("/addresses/shipping/{_id}", response_model=ShippingAddress)
def create_update_shipping_address(
    data: AddressCreate,
    partner:Annotated[ResPartner, Depends(authenticated_partner)],
    _id: int | None = None,
) -> ShippingAddress:
    """
    Create/Update shipping address of authenticated user
    """
    vals = data.to_res_partner_vals()
    if _id is None:
        address = partner._create_shopinvader_shipping_address(vals)
    else:
        address = partner._update_shopinvader_shipping_address(vals, _id)
    return ShippingAddress.from_res_partner(address)


@address_router.delete("/addresses/shipping/{_id}")
def delete_shipping_address(
    _id: int,
    partner:Annotated[ResPartner, Depends(authenticated_partner)],
) -> None:
    """
    Delete shipping address of authenticated user
    Address will be archive
    """
    partner._delete_shopinvader_shipping_address(_id)