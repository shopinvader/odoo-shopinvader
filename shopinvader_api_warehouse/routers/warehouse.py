# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import api, fields

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.extendable_fastapi.schemas import PagedCollection
from odoo.addons.fastapi.dependencies import (
    optionally_authenticated_partner,
    optionally_authenticated_partner_env,
    paging,
)
from odoo.addons.fastapi.schemas import Paging
from odoo.addons.shopinvader_router_helper import VirtualModel

from ..schemas.warehouse import Warehouse, WarehouseSearch

warehouse_router = APIRouter(tags=["warehouses"])


class WarehouseHelper(VirtualModel):
    _inherit = "shopinvader.router.helper"
    _name = "shopinvader_api_warehouse.warehouse_router.helper"
    _description = "Shopinvader Api Warehouse Service Helper"
    _model = "stock.warehouse"

    partner = fields.Many2one("res.partner")

    def _domain(self):
        return []


def warehouse_helper(
    env: Annotated[api.Environment, Depends(optionally_authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(optionally_authenticated_partner)],
):
    return env["shopinvader_api_warehouse.warehouse_router.helper"].new(
        {"partner": partner}
    )


@warehouse_router.get("/warehouses")
def search(
    params: Annotated[WarehouseSearch, Depends()],
    paging: Annotated[Paging, Depends(paging)],
    helper: Annotated[WarehouseHelper, Depends(warehouse_helper)],
) -> PagedCollection[Warehouse]:
    """Get / search warehouses. The list contains only warehouses accessible to
    the authenticated user"""
    count, warehouses = helper.search_with_count(
        params.to_odoo_domain(helper.env),
        limit=paging.limit,
        offset=paging.offset,
    )
    return PagedCollection[Warehouse](
        count=count,
        items=[
            Warehouse.from_stock_warehouse(warehouse, helper.partner)
            for warehouse in warehouses
        ],
    )


@warehouse_router.get("/warehouses/{warehouse_id}")
def get(
    warehouse_id: int,
    helper: Annotated[WarehouseHelper, Depends(warehouse_helper)],
) -> Warehouse:
    """
    Get warehouse details with specific warehouse_id
    """
    return Warehouse.from_stock_warehouse(
        helper.get(warehouse_id),
        helper.partner,
    )
