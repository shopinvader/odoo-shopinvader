from fastapi import APIRouter, Depends

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import authenticated_partner_env, paging
from odoo.addons.fastapi.schemas import PagedCollection, Paging
from odoo.addons.shopinvader_schema_address.schema import Address

from ..schema import AddressInput, AddressSearch

# create a router
address_router = APIRouter()


@address_router.post(
    "/address/create", response_model=PagedCollection[Address], status_code=201
)
def address_create(
    data: AddressInput,
    env: Environment = Depends(authenticated_partner_env),
) -> PagedCollection[Address]:
    """
    Create new address and link it to authenticated partner
    """
    address = env["res.partner"]._create_shopinvader_address(data)
    return PagedCollection[Address](
        total=len(address),
        items=[Address.from_orm(rec) for rec in address],
    )


@address_router.get("/address/{rec_id}", response_model=PagedCollection[Address])
def address_get(
    rec_id: int,
    env: Environment = Depends(authenticated_partner_env),
) -> PagedCollection[Address]:
    """
    Get a specific address using id
    """
    address = env["res.partner"]._get_shopinvader_address(rec_id)
    return PagedCollection[Address](
        total=len(address),
        items=[Address.from_orm(rec) for rec in address],
    )


@address_router.post("/address/search", response_model=PagedCollection[Address])
def address_search(
    query: AddressSearch = Depends(),
    paging: Paging = Depends(paging),
    env: Environment = Depends(authenticated_partner_env),
) -> PagedCollection[Address]:
    """
    Perform a search on addresses
    """
    address = env["res.partner"]._search_shopinvader_address(
        query, limit=paging.limit, offset=paging.offset
    )
    return PagedCollection[Address](
        total=len(address),
        items=[Address.from_orm(rec) for rec in address],
    )


@address_router.delete("/address/{rec_id}")
def address_delete(
    rec_id: int,
    env: Environment = Depends(authenticated_partner_env),
) -> None:
    """
    Delete address using record id to identify address
    """
    env["res.partner"]._delete_shopinvader_address(rec_id)

    # Billing address

    # Shipping address

    """
    TODO:
     no delete only archive
     billing addres is on authenticated partner and unique
     prevent modifing billing address if account move created
     shipping address: create/unlink
    """
