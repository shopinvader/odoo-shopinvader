from fastapi import APIRouter, Depends

from odoo.api import Environment

from odoo import api,models
from odoo.addons.fastapi.dependencies import authenticated_partner_env, authenticated_partner
from odoo.addons.fastapi.schemas import PagedCollection
from odoo.addons.shopinvader_schema_address.schemas import BillingAddress, ShippingAddress

from ..schemas import AddressInput, AddressUpdate

# create a router
address_router = APIRouter()

#### Billing address ####
    
@address_router.get("/addresses/billing", response_model=BillingAddress)
def get_billing_address(
    env: Environment = Depends(authenticated_partner_env),
    partner = Depends(authenticated_partner),
) -> BillingAddress:
    """
    Get billing address of authenticated user
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
    Update billing address of authenticated user
    billing address corresponds to authenticated partner
    """
    address_id = env["res.partner"]._update_shopinvader_billing_address(partner,data)
    return BillingAddress.from_orm(address_id)

#### Shipping address ####

@address_router.get("/addresses/shipping", response_model=PagedCollection[ShippingAddress])
@address_router.get("/addresses/shipping/{id}", response_model=PagedCollection[ShippingAddress])
def get_shipping_address(
    env: Environment = Depends(authenticated_partner_env),
    partner = Depends(authenticated_partner),
    id: int | None = None,
) -> PagedCollection[ShippingAddress]:
    """
    Get shipping addresses of authenticated user
    Can be used to get every shipping address: /addresses/shipping
    Can be used to get one specific address: /addresses/shipping/rec_id
    """
    address_ids = env["res.partner"]._get_shopinvader_shipping_address(partner,id)
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
    Create/Update shipping address of authenticated user
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
        Delete shipping address of authenticated user
        Address will be archive
    """
    env["res.partner"]._delete_shipping_address(id)


# Mapper
class ShopinvaderApiAddressMapper(models.AbstractModel):
    _name = 'shopinvader_api_address.mapper'
    _description = 'Shopinvader Api Address Mapper'

    @api.model
    def _addressInput_to_res_partner(self, data: AddressInput) -> dict:

        vals = {
            "name": data.name or "",
            "street": data.street or "",
            "street2": data.street2 or "",
            "zip": data.zip or "",
            "city": data.city or "",
            "phone": data.phone or "",
            "email": data.email or "",
            "state_id": data.state or None,
            "country_id": data.country or None,
        }
        return vals
    
    @api.model
    def _addressupdate_to_res_partner(self, data: AddressUpdate) -> dict:
        vals={}
        if data.name is not None:
            vals["name"] = data.name
        if data.street is not None:
            vals["street"] = data.street
        if data.street2 is not None:
            vals["street2"] = data.street2
        if data.zip is not None:
            vals["zip"] = data.zip
        if data.city is not None:
            vals["city"] = data.city
        if data.phone is not None:
            vals["phone"] = data.phone
        if data.email is not None:
            vals["email"] = data.email

        if data.country is not None:
            vals["country_id"] = data.country
        if data.state is not None:
            vals["state_id"] = data.state
        return vals