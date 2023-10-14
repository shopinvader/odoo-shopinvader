from typing import Annotated, List

from fastapi import APIRouter, Depends

from odoo import api

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
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


@address_router.get("/addresses/billing")
def get_billing_addresses(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> List[BillingAddress]:
    """
    Get billing address of authenticated user
    billing address corresponds to authenticated partner
    """
    address = env["shopinvader_address.service.helper"]._get_billing_addresses(partner)
    return [BillingAddress.from_res_partner(rec) for rec in address]


@address_router.get("/addresses/billing/{address_id}")
def get_billing_address(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    address_id: int,
) -> BillingAddress:
    """
    Get billing address of authenticated user with specific address_id
    billing address corresponds to authenticated partner
    """
    address = env["shopinvader_address.service.helper"]._get_billing_address(
        partner, address_id
    )
    return BillingAddress.from_res_partner(address)


@address_router.post("/addresses/billing", status_code=201)
def create_billing_address(
    data: BillingAddressCreate,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> BillingAddress:
    """
    Create billing address
    Raise error since billing address is the authenticated partner
    """
    vals = data.to_res_partner_vals()
    address = env[
        "shopinvader_address.service.helper"
    ]._create_shopinvader_billing_address(partner, vals)
    return BillingAddress.from_res_partner(address)


@address_router.post("/addresses/billing/{address_id}")
def update_billing_address(
    data: BillingAddressUpdate,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
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
    address = (
        env["shopinvader_address.service.helper"]
        .sudo()
        ._update_billing_address(partner, vals, address_id)
    )
    return BillingAddress.from_res_partner(address)


# --- Shipping address ---


@address_router.get("/addresses/shipping")
def get_shipping_addresses(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> List[ShippingAddress]:
    """
    Get shipping addresses of authenticated user
    Can be used to get every shipping address: /addresses/shipping
    """
    addresses = env["shopinvader_address.service.helper"]._get_shipping_addresses(
        partner
    )
    return [ShippingAddress.from_res_partner(rec) for rec in addresses]


@address_router.get("/addresses/shipping/{address_id}")
def get_shipping_address(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    address_id: int,
) -> ShippingAddress:
    """
    Get shipping addresses of authenticated user
    Can be used to get one specific address: /addresses/shipping/address_id
    """
    addresses = env["shopinvader_address.service.helper"]._get_shipping_address(
        partner, address_id
    )
    return ShippingAddress.from_res_partner(addresses)


@address_router.post("/addresses/shipping", status_code=201)
def create_shipping_address(
    data: ShippingAddressCreate,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> ShippingAddress:
    """
    Create shipping address of authenticated user
    """
    vals = data.to_res_partner_vals()
    address = env["shopinvader_address.service.helper"]._create_shipping_address(
        partner, vals
    )

    return ShippingAddress.from_res_partner(address)


@address_router.post("/addresses/shipping/{address_id}")
def update_shipping_address(
    data: ShippingAddressUpdate,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
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
    address = (
        env["shopinvader_address.service.helper"]
        .sudo()
        ._update_shipping_address(partner, vals, address_id)
    )
    return ShippingAddress.from_res_partner(address)


@address_router.delete("/addresses/shipping/{address_id}")
def delete_shipping_address(
    address_id: int,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
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
    env["shopinvader_address.service.helper"].sudo()._delete_shipping_address(
        partner, address_id
    )
