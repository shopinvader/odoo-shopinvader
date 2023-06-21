from fastapi import APIRouter, Depends

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import authenticated_partner_env, paging, authenticated_partner
from odoo.addons.fastapi.schemas import PagedCollection, Paging
from odoo.addons.shopinvader_schema_address.schemas import Address, BillingAddress, ShippingAddress

from ..schemas import AddressInput, AddressSearch, AddressUpdate

# create a router
address_router = APIRouter()

#### Billing address ####
    
@address_router.get("/address/billing", response_model=BillingAddress)
def address_get_billing(
    env: Environment = Depends(authenticated_partner_env),
    partner = Depends(authenticated_partner),
) -> BillingAddress:
    """
    Get billing address
    billing address corresponds to authenticated partner
    """
    address_id = env["res.partner"]._get_shopinvader_billing_address(partner)
    return BillingAddress.from_orm(address_id)

@address_router.post("/address/billing", response_model=BillingAddress,status_code=201)
def address_update_billing(
    data: AddressUpdate,
    env: Environment = Depends(authenticated_partner_env),
    partner = Depends(authenticated_partner),
) -> BillingAddress:
    """
    Update billing address
    billing address corresponds to authenticated partner
    """
    address_id = env["res.partner"]._update_shopinvader_billing_address(partner,data)
    return BillingAddress.from_orm(address_id)

#### Shipping address ####

@address_router.get("/address/shipping", response_model=PagedCollection[ShippingAddress])
@address_router.get("/address/shipping/{rec_id}", response_model=PagedCollection[ShippingAddress])
def address_get_shipping(
    env: Environment = Depends(authenticated_partner_env),
    rec_id: int | None = None,
) -> PagedCollection[ShippingAddress]:
    """
    Get shipping addresses
    """
    address_ids = env["res.partner"]._get_shopinvader_shipping_address(rec_id)
    return  PagedCollection[ShippingAddress](
        total=len(address_ids),
        items=[ShippingAddress.from_orm(rec) for rec in address_ids],
    )

@address_router.post("/address/shipping", response_model=ShippingAddress,status_code=201)
@address_router.post("/address/shipping/{rec_id}", response_model=ShippingAddress)
def address_create_update_shipping(
    data: AddressInput,
    env: Environment = Depends(authenticated_partner_env),
    partner = Depends(authenticated_partner),
    rec_id:int|None = None,
) -> ShippingAddress:
    """
    Create/Update shipping address
    """
    if rec_id is None:
        address_id = env["res.partner"]._create_shipping_address(partner,data)
    else:
        address_id = env["res.partner"]._update_shipping_address(data,rec_id)
    return ShippingAddress.from_orm(address_id)

@address_router.delete("/address/shipping/{rec_id}")
def address_delete_shipping(
    rec_id: int,
    env: Environment = Depends(authenticated_partner_env),
)-> None:
    """
        Delete shipping address
        Address will be archive
    """
    env["res.partner"]._delete_shipping_address(rec_id)