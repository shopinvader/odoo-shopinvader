from fastapi import APIRouter, Depends

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import authenticated_partner_env, authenticated_partner
from odoo.addons.fastapi.schemas import PagedCollection
from odoo.addons.shopinvader_schema_address.schemas import BillingAddress, ShippingAddress

from ..schemas import AddressInput, AddressSearch, AddressUpdate

# create a router
address_router = APIRouter()

#### Billing address ####
    
@address_router.get("/addresses/billing", response_model=BillingAddress)
def get_billing_address(
    env: Environment = Depends(authenticated_partner_env),
    partner = Depends(authenticated_partner),
) -> BillingAddress:
    """
    Get billing address
    billing address corresponds to authenticated partner
    """
    address_id = env["res.partner"]._get_shopinvader_billing_address(partner)
    return BillingAddress.from_orm(address_id)

@address_router.post("/addresses/billing", response_model=BillingAddress,status_code=201)
def update_billing_address(
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

@address_router.get("/addresses/shipping", response_model=PagedCollection[ShippingAddress])
@address_router.get("/addresses/shipping/{id}", response_model=PagedCollection[ShippingAddress])
def get_shipping_address(
    env: Environment = Depends(authenticated_partner_env),
    id: int | None = None,
    data: AddressSearch = Depends(AddressSearch),
) -> PagedCollection[ShippingAddress]:
    """
    Get shipping addresses
    Can be used to get every shipping address: /addresses/shipping
    Can be used to get one specific address: /addresses/shipping/rec_id
    If an AddressSearch is given, it will act as a search with given filter
    """
    address_ids = env["res.partner"]._get_shopinvader_shipping_address(id,data)
    return  PagedCollection[ShippingAddress](
        total=len(address_ids),
        items=[ShippingAddress.from_orm(rec) for rec in address_ids],
    )

@address_router.post("/addresses/shipping", response_model=ShippingAddress,status_code=201)
@address_router.post("/addresses/shipping/{id}", response_model=ShippingAddress)
def create_update_shipping_address(
    data: AddressInput,
    env: Environment = Depends(authenticated_partner_env),
    partner = Depends(authenticated_partner),
    id:int|None = None,
) -> ShippingAddress:
    """
    Create/Update shipping address
    """
    if id is None:
        address_id = env["res.partner"]._create_shipping_address(partner,data)
    else:
        address_id = env["res.partner"]._update_shipping_address(data,id)
    return ShippingAddress.from_orm(address_id)

@address_router.delete("/addresses/shipping/{id}")
def delete_shipping_address(
    id: int,
    env: Environment = Depends(authenticated_partner_env),
)-> None:
    """
        Delete shipping address
        Address will be archive
    """
    env["res.partner"]._delete_shipping_address(id)