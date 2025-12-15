# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import api, fields, models

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.extendable_fastapi.schemas import PagedCollection
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
    paging,
)
from odoo.addons.fastapi.schemas import Paging
from odoo.addons.shopinvader_filtered_model.utils import FilteredModelAdapter
from odoo.addons.stock.models.stock_warehouse import Warehouse as StockWarehouse

from ..schemas.warehouse import Warehouse, WarehouseSearch

warehouse_router = APIRouter(tags=["warehouses"])


@warehouse_router.get("/warehouses")
def search(
    params: Annotated[WarehouseSearch, Depends()],
    paging: Annotated[Paging, Depends(paging)],
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> PagedCollection[Warehouse]:
    """Get / search warehouses. The list contains only warehouses accessible to
    the authenticated user"""
    count, warehouses = (
        env["shopinvader_api_warehouse.warehouse_router.helper"]
        .new({"partner": partner})
        ._search(paging, params)
    )
    return PagedCollection[Warehouse](
        count=count,
        items=[
            Warehouse.from_stock_warehouse(warehouse, partner)
            for warehouse in warehouses
        ],
    )


@warehouse_router.get("/warehouses/{warehouse_id}")
def get(
    warehouse_id: int,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> Warehouse:
    """
    Get warehouse details with specific warehouse_id
    """
    return Warehouse.from_stock_warehouse(
        env["shopinvader_api_warehouse.warehouse_router.helper"]
        .new({"partner": partner})
        ._get(warehouse_id),
        partner,
    )


class ShopinvaderApiWarehouseRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_warehouse.warehouse_router.helper"
    _description = "Shopinvader Api Warehouse Service Helper"

    partner = fields.Many2one("res.partner")

    def _get_domain_adapter(self):
        """This method is meant to be overridden to provide specific domain
        filters based on the context (for example the authenticated user)"""
        return []

    @property
    def model_adapter(self) -> FilteredModelAdapter[StockWarehouse]:
        return FilteredModelAdapter[StockWarehouse](
            self.env, self._get_domain_adapter()
        )

    def _get(self, record_id) -> StockWarehouse:
        return self.model_adapter.get(record_id)

    def _search(self, paging, params) -> tuple[int, StockWarehouse]:
        return self.model_adapter.search_with_count(
            params.to_odoo_domain(self.env),
            limit=paging.limit,
            offset=paging.offset,
        )
