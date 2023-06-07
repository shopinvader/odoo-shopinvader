from fastapi import Depends

from odoo.api import Environment

from odoo.addons.fastapi.depends import authenticated_partner_env, paging,odoo_env
from odoo.addons.fastapi.schemas import PagedCollection, Paging
from odoo.addons.shopinvader_schema_address.schema.address import Address
from ..schema.schema import AddressSearch,AddressInput

from ..models.fast_api_endpoint import address_api_router

from typing import Optional


@address_api_router.get("/partners", response_model=PagedCollection[Address])
def get_address(
    paging: Paging = Depends(paging),
    env: Environment = Depends(authenticated_partner_env),
) -> PagedCollection[Address]:
    """Get the list of Address"""
    count = env["res.partner"].search_count([])
    partners = (
        env["res.partner"].search([], limit=paging.limit, offset=paging.offset)
    )
    return PagedCollection[Address](
        total=count,
        items=[Address.from_orm(rec) for rec in partners],
    )

@address_api_router.get("/address/{uuid}",response_model=PagedCollection[Address])
def addres_get(
    uuid: int,
    env: Environment = Depends(authenticated_partner_env),
) -> PagedCollection[Address]:
    address = env["res.partner"].search([("id","=",uuid)], limit=1)
    count = len(address)
    return PagedCollection[Address](
        total=count,
        items=[Address.from_orm(rec) for rec in address],
    )

@address_api_router.get("/address/search",response_model=PagedCollection[Address])
def address_search(
    query: AddressSearch = Depends(),
    paging: Paging = Depends(paging),
    env: Environment = Depends(authenticated_partner_env),
) -> PagedCollection[Address]:
    address = env["res.partner"]._search_shopinvader_address(query, limit=paging.limit, offset=paging.offset)
    return PagedCollection[Address](
        total=len(address),
        items=[Address.from_orm(rec) for rec in address],
    )

@address_api_router.post(
    "/address/create", response_model=PagedCollection[Address], status_code=201
)
def address_create(
    data: AddressInput,
    env: Environment = Depends(odoo_env),
) -> PagedCollection[Address]:
    address = env["res.partner"]._create_shopinvader_address(data)
    return PagedCollection[Address](
        total=len(address),
        items=[Address.from_orm(rec) for rec in address],
    )
