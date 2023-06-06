from typing import Annotated, List

from fastapi import APIRouter, Depends

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import authenticated_partner
from odoo.addons.shopinvader_schema_address.schemas import (
    BillingAddress,
    ShippingAddress,
)

from ..schemas import (
    BillingAddressCreate,
    BillingAddressUpdate,
    ShippingAddressCreate,
    ShippingAddressUpdate,
)

# create a router
address_router = APIRouter(tags=["addresses"])

# --- Billing addresses ---


@address_router.get("/addresses/billing", response_model=List[BillingAddress])
def get_billing_addresses(
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> List[BillingAddress]:
    """
    Get billing address of authenticated user
    billing address corresponds to authenticated partner
    """
    address = partner._get_shopinvader_billing_addresses()
    return [BillingAddress.from_res_partner(rec) for rec in address]


@address_router.get("/addresses/billing/{address_id}", response_model=BillingAddress)
def get_billing_address(
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    address_id: int,
) -> BillingAddress:
    """
    Get billing address of authenticated user with specific address_id
    billing address corresponds to authenticated partner
    """
    address = partner._get_shopinvader_billing_address(address_id)
    return BillingAddress.from_res_partner(address)


@address_router.post(
    "/addresses/billing", response_model=BillingAddress, status_code=201
)
def create_billing_address(
    data: BillingAddressCreate,
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> BillingAddress:
    """
    Create billing address
    Raise error since billing address is the authenticated partner
    """
    vals = data.to_res_partner_vals()
    address = partner._create_shopinvader_billing_address(vals)
    return BillingAddress.from_res_partner(address)


@address_router.post("/addresses/billing/{address_id}", response_model=BillingAddress)
def update_billing_address(
    data: BillingAddressUpdate,
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    address_id: int,
) -> BillingAddress:
    """
    Update billing address of authenticated user
    billing address corresponds to authenticated partner
    """
    vals = data.to_res_partner_vals()
    # sudo() is needed because some addons override the write
    # function of res.partner to do some checks before writing.
    # These checks need more rights than what we are giving to
    # the enspoint's user
    # (e.g. snailmail/models/res_partner.py)
    address = partner.sudo()._update_shopinvader_billing_address(vals, address_id)
    return BillingAddress.from_res_partner(address)


# --- Shipping address ---


@address_router.get("/addresses/shipping", response_model=List[ShippingAddress])
def get_shipping_addresses(
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> List[ShippingAddress]:
    """
    Get shipping addresses of authenticated user
    Can be used to get every shipping address: /addresses/shipping
    """
    addresses = partner._get_shopinvader_shipping_addresses()
    return [ShippingAddress.from_res_partner(rec) for rec in addresses]


@address_router.get("/addresses/shipping/{address_id}", response_model=ShippingAddress)
def get_shipping_address(
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    address_id: int,
) -> ShippingAddress:
    """
    Get shipping addresses of authenticated user
    Can be used to get one specific address: /addresses/shipping/address_id
    """
    addresses = partner._get_shopinvader_shipping_address(address_id)
    return ShippingAddress.from_res_partner(addresses)


@address_router.post(
    "/addresses/shipping", response_model=ShippingAddress, status_code=201
)
def create_shipping_address(
    data: ShippingAddressCreate,
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> ShippingAddress:
    """
    Create shipping address of authenticated user
    """
    vals = data.to_res_partner_vals()
    address = partner._create_shopinvader_shipping_address(vals)

    return ShippingAddress.from_res_partner(address)


@address_router.post("/addresses/shipping/{address_id}", response_model=ShippingAddress)
def update_shipping_address(
    data: ShippingAddressUpdate,
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    address_id: int,
) -> ShippingAddress:
    """
    Update shipping address of authenticated user
    """
    vals = data.to_res_partner_vals()
    # sudo() is needed because some addons override the write
    # function of res.partner to do some checks before writing.
    # These checks need more rights than what we are giving to
    # the enspoint's user
    # (e.g. snailmail/models/res_partner.py)
    address = partner.sudo()._update_shopinvader_shipping_address(vals, address_id)
    return ShippingAddress.from_res_partner(address)


@address_router.delete("/addresses/shipping/{address_id}")
def delete_shipping_address(
    address_id: int,
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> None:
    """
    Delete shipping address of authenticated user
    Address will be archived.
    """

    # sudo() is needed because some addons override the write
    # function of res.partner to do some checks before writing.
    # These checks need more rights than what we are giving to
    # the enspoint's user
    # (e.g. snailmail/models/res_partner.py)
    partner.sudo()._delete_shopinvader_shipping_address(address_id)
