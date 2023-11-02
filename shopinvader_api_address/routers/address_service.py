from typing import Annotated, List

from fastapi import APIRouter, Depends

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import authenticated_partner
from odoo.addons.shopinvader_schema_address.schemas import (
    DeliveryAddress,
    InvoicingAddress,
)

from ..schemas import (
    DeliveryAddressCreate,
    DeliveryAddressUpdate,
    InvoicingAddressCreate,
    InvoicingAddressUpdate,
)

# create a router
address_router = APIRouter(tags=["addresses"])

# --- Invoicing addresses ---


@address_router.get("/addresses/invoicing", response_model=List[InvoicingAddress])
def get_invoicing_addresses(
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> List[InvoicingAddress]:
    """
    Get invoicing address of authenticated user
    invoicing address corresponds to authenticated partner
    """
    address = partner._get_shopinvader_invoicing_addresses()
    return [InvoicingAddress.from_res_partner(rec) for rec in address]


@address_router.get(
    "/addresses/invoicing/{address_id}", response_model=InvoicingAddress
)
def get_invoicing_address(
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    address_id: int,
) -> InvoicingAddress:
    """
    Get invoicing address of authenticated user with specific address_id
    invoicing address corresponds to authenticated partner
    """
    address = partner._get_shopinvader_invoicing_address(address_id)
    return InvoicingAddress.from_res_partner(address)


@address_router.post(
    "/addresses/invoicing", response_model=InvoicingAddress, status_code=201
)
def create_invoicing_address(
    data: InvoicingAddressCreate,
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> InvoicingAddress:
    """
    Create invoicing address
    Raise error since invoicing address is the authenticated partner
    """
    vals = data.to_res_partner_vals()
    address = partner._create_shopinvader_invoicing_address(vals)
    return InvoicingAddress.from_res_partner(address)


@address_router.post(
    "/addresses/invoicing/{address_id}", response_model=InvoicingAddress
)
def update_invoicing_address(
    data: InvoicingAddressUpdate,
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    address_id: int,
) -> InvoicingAddress:
    """
    Update invoicing address of authenticated user
    invoicing address corresponds to authenticated partner
    """
    vals = data.to_res_partner_vals()
    # sudo() is needed because some addons override the write
    # function of res.partner to do some checks before writing.
    # These checks need more rights than what we are giving to
    # the enspoint's user
    # (e.g. snailmail/models/res_partner.py)
    address = partner.sudo()._update_shopinvader_invoicing_address(vals, address_id)
    return InvoicingAddress.from_res_partner(address)


# --- Delivery address ---


@address_router.get("/addresses/delivery", response_model=List[DeliveryAddress])
def get_delivery_addresses(
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> List[DeliveryAddress]:
    """
    Get delivery addresses of authenticated user
    Can be used to get every delivery address: /addresses/delivery
    """
    addresses = partner._get_shopinvader_delivery_addresses()
    return [DeliveryAddress.from_res_partner(rec) for rec in addresses]


@address_router.get("/addresses/delivery/{address_id}", response_model=DeliveryAddress)
def get_delivery_address(
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    address_id: int,
) -> DeliveryAddress:
    """
    Get delivery addresses of authenticated user
    Can be used to get one specific address: /addresses/delivery/address_id
    """
    addresses = partner._get_shopinvader_delivery_address(address_id)
    return DeliveryAddress.from_res_partner(addresses)


@address_router.post(
    "/addresses/delivery", response_model=DeliveryAddress, status_code=201
)
def create_delivery_address(
    data: DeliveryAddressCreate,
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> DeliveryAddress:
    """
    Create delivery address of authenticated user
    """
    vals = data.to_res_partner_vals()
    address = partner._create_shopinvader_delivery_address(vals)

    return DeliveryAddress.from_res_partner(address)


@address_router.post("/addresses/delivery/{address_id}", response_model=DeliveryAddress)
def update_delivery_address(
    data: DeliveryAddressUpdate,
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
    address_id: int,
) -> DeliveryAddress:
    """
    Update delivery address of authenticated user
    """
    vals = data.to_res_partner_vals()
    # sudo() is needed because some addons override the write
    # function of res.partner to do some checks before writing.
    # These checks need more rights than what we are giving to
    # the enspoint's user
    # (e.g. snailmail/models/res_partner.py)
    address = partner.sudo()._update_shopinvader_delivery_address(vals, address_id)
    return DeliveryAddress.from_res_partner(address)


@address_router.delete("/addresses/delivery/{address_id}")
def delete_delivery_address(
    address_id: int,
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> None:
    """
    Delete delivery address of authenticated user
    Address will be archived.
    """

    # sudo() is needed because some addons override the write
    # function of res.partner to do some checks before writing.
    # These checks need more rights than what we are giving to
    # the enspoint's user
    # (e.g. snailmail/models/res_partner.py)
    partner.sudo()._delete_shopinvader_delivery_address(address_id)
