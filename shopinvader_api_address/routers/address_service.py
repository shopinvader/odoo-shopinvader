from fastapi import APIRouter, Depends

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import authenticated_partner_env, paging, authenticated_partner
from odoo.addons.fastapi.schemas import PagedCollection, Paging
from odoo.addons.shopinvader_schema_address.schema import Address, BillingAddress, ShippingAddress

from ..schema import AddressInput, AddressSearch, AddressUpdate

# create a router
address_router = APIRouter()


# @address_router.post(
#     "/address/create", response_model=PagedCollection[Address], status_code=201
# )
# def address_create(
#     data: AddressInput,
#     env: Environment = Depends(authenticated_partner_env),
# ) -> PagedCollection[Address]:
#     """
#     Create new address and link it to authenticated partner
#     """
#     address = env["res.partner"]._create_shopinvader_address(data)
#     return PagedCollection[Address](
#         total=len(address),
#         items=[Address.from_orm(rec) for rec in address],
#     )


# @address_router.get("/address/{rec_id}", response_model=PagedCollection[Address])
# def address_get(
#     rec_id: int,
#     env: Environment = Depends(authenticated_partner_env),
# ) -> PagedCollection[Address]:
#     """
#     Get a specific address using id
#     """
#     address = env["res.partner"]._get_shopinvader_address(rec_id)
#     return PagedCollection[Address](
#         total=len(address),
#         items=[Address.from_orm(rec) for rec in address],
#     )


# @address_router.post("/address/search", response_model=PagedCollection[Address])
# def address_search(
#     query: AddressSearch = Depends(),
#     paging: Paging = Depends(paging),
#     env: Environment = Depends(authenticated_partner_env),
# ) -> PagedCollection[Address]:
#     """
#     Perform a search on addresses
#     """
#     address = env["res.partner"]._search_shopinvader_address(
#         query, limit=paging.limit, offset=paging.offset
#     )
#     return PagedCollection[Address](
#         total=len(address),
#         items=[Address.from_orm(rec) for rec in address],
#     )


# @address_router.delete("/address/{rec_id}")
# def address_delete(
#     rec_id: int,
#     env: Environment = Depends(authenticated_partner_env),
# ) -> None:
#     """
#     Delete address using record id to identify address
#     """
#     env["res.partner"]._delete_shopinvader_address(rec_id)

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
def address_create_shipping(
    data: AddressUpdate,
    env: Environment = Depends(authenticated_partner_env),
    partner = Depends(authenticated_partner),
) -> ShippingAddress:
    """
    Update billing address
    billing address corresponds to authenticated partner
    """
    address_id = env["res.partner"]._create_shipping_address(partner,data)
    return ShippingAddress.from_orm(address_id)