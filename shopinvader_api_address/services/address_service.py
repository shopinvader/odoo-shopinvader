from fastapi import Depends

from odoo.api import Environment

from odoo.addons.fastapi.depends import odoo_env, paging
from odoo.addons.fastapi.schemas import PagedCollection, Paging
from odoo.addons.shopinvader_schema_address.schema.address import Address

from ..models.fast_api_endpoint import address_api_router


@address_api_router.get("/", response_model=PagedCollection[Address])
def get_address(
    paging: Paging = Depends(paging),
    env: Environment = Depends(odoo_env),  # use authenticated_partner_env
) -> PagedCollection[Address]:
    """Get the list of Address"""
    count = env["res.partner"].search_count([])
    partners = (
        env["res.partner"].sudo().search([], limit=paging.limit, offset=paging.offset)
    )
    return PagedCollection[Address](
        total=count,
        items=[Address.from_orm(rec) for rec in partners],
    )
