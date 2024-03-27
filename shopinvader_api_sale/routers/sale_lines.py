# Copyright 2024 Akretion (http://www.akretion.com).
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
from odoo.addons.sale.models.sale_order_line import SaleOrderLine
from odoo.addons.shopinvader_filtered_model.utils import FilteredModelAdapter

from ..schemas import SaleLineSearch, SaleLineWithSale

sale_line_router = APIRouter(tags=["sales"])


@sale_line_router.get("/sale_lines")
def search(
    params: Annotated[SaleLineSearch, Depends()],
    paging: Annotated[Paging, Depends(paging)],
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> PagedCollection[SaleLineWithSale]:
    """Get / search sale order lines. The list contains only sale order lines from the
    authenticated user"""
    count, sols = (
        env["shopinvader_api_sale.sale_line_router.helper"]
        .new({"partner": partner})
        ._search(paging, params)
    )
    return PagedCollection[SaleLineWithSale](
        count=count,
        items=[SaleLineWithSale.from_sale_order_line(sol) for sol in sols],
    )


@sale_line_router.get("/sale_lines/{sale_line_id}")
def get(
    sale_line_id: int,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> SaleLineWithSale:
    """
    Get sale order of authenticated user with specific sale_id
    """
    return SaleLineWithSale.from_sale_order_line(
        env["shopinvader_api_sale.sale_line_router.helper"]
        .new({"partner": partner})
        ._get(sale_line_id)
    )


class ShopinvaderApiSaleSaleLineRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_sale.sale_line_router.helper"
    _description = "Shopinvader Api Sale Line Service Helper"

    partner = fields.Many2one("res.partner")

    def _get_domain_adapter(self):
        return [
            ("order_id.partner_id", "=", self.partner.id),
            ("order_id.typology", "=", "sale"),
        ]

    @property
    def model_adapter(self) -> FilteredModelAdapter[SaleOrderLine]:
        return FilteredModelAdapter[SaleOrderLine](self.env, self._get_domain_adapter())

    def _get(self, record_id) -> SaleOrderLine:
        return self.model_adapter.get(record_id)

    def _search(self, paging, params) -> tuple[int, SaleOrderLine]:
        return self.model_adapter.search_with_count(
            params.to_odoo_domain(self.env),
            limit=paging.limit,
            offset=paging.offset,
        )
