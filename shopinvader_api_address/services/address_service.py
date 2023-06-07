from fastapi import Depends

from odoo.api import Environment

from odoo.addons.fastapi.depends import authenticated_partner_env, paging,odoo_env
from odoo.addons.fastapi.schemas import PagedCollection, Paging
from odoo.addons.shopinvader_schema_address.schema.address import Address

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

@address_api_router.get("/{uuid}",response_model=PagedCollection[Address])
def get(
    uuid: int,
    env: Environment = Depends(odoo_env),
) -> PagedCollection[Address]:
    address = env["res.partner"].search([("id","=",uuid)], limit=1)
    count = len(address)
    return PagedCollection[Address](
        total=count,
        items=[Address.from_orm(rec) for rec in address],
    )

@address_api_router.post("/{uuid}",response_model=PagedCollection[Address])
def create(
    
)