# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import api

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
    paging,
)
from odoo.addons.fastapi.schemas import PagedCollection, Paging
from odoo.addons.sale.models.sale_order import SaleOrder

from ..schemas import SaleOrderSearch

sale_router = APIRouter(tags=["sales"])


@sale_router.get("/sales/")
def search(
    sale_search_params: Annotated[SaleOrderSearch, Depends()],
    paging: Annotated[Paging, Depends(paging)],
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated["ResPartner", Depends(authenticated_partner)],
) -> PagedCollection[SaleOrder]:
    """Get the list of sale orders."""
    domain = SaleOrderSearch.to_domain()
    count = env["sale.order"].search_count(domain)
    orders = env["sale.order"].search(domain, limit=paging.limit, offset=paging.offset)
    return PagedCollection[SaleOrder](
        total=count,
        items=[SaleOrder.model_validate(order) for order in orders],
    )
