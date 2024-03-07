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
from odoo.addons.shopinvader_api_unit_member.routers.unit_members import (
    authenticated_manager,
)
from odoo.addons.shopinvader_filtered_model.utils import FilteredModelAdapter

from ..schemas import RejectRequest, RequestedSaleLine, RequestedSaleLineSearch

unit_request_line_router = APIRouter(tags=["unit"])


@unit_request_line_router.get("/unit/request_lines")
async def get_request_lines(
    params: Annotated[RequestedSaleLineSearch, Depends()],
    paging: Annotated[Paging, Depends(paging)],
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> PagedCollection[RequestedSaleLine]:
    """
    Get list of requested sale lines
    """
    count, sols = (
        env["shopinvader_api_unit_request.lines.helper"]
        .new({"partner": partner})
        ._search(paging, params)
    )
    return PagedCollection[RequestedSaleLine](
        count=count,
        items=[RequestedSaleLine.from_sale_order_line(sol) for sol in sols],
    )


@unit_request_line_router.get("/unit/request_lines/{id}")
async def get_requested_sale_line(
    id: int,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_manager)],
) -> RequestedSaleLine:
    """
    Get a specific requested sale line
    """
    return RequestedSaleLine.from_sale_order_line(
        env["shopinvader_api_unit_request.lines.helper"]
        .new({"partner": partner})
        ._get(id)
    )


@unit_request_line_router.post("/unit/request_lines/{id}/accept")
async def accept_requested_sale_line(
    id: int,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_manager)],
) -> RequestedSaleLine:
    """
    Accept a specific requested sale line
    """
    sale_line = (
        env["shopinvader_api_unit_request.lines.helper"]
        .new({"partner": partner})
        ._get(id)
    )
    cart = env["sale.order"]._find_open_cart(partner.id)
    sale_line._action_accept_request(cart)
    return RequestedSaleLine.from_sale_order_line(sale_line)


@unit_request_line_router.post("/unit/request_lines/{id}/reject")
async def reject_requested_sale_line(
    id: int,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    data: RejectRequest,
    partner: Annotated[ResPartner, Depends(authenticated_manager)],
) -> RequestedSaleLine:
    """
    Reject a specific requested sale line
    """
    sale_line = (
        env["shopinvader_api_unit_request.lines.helper"]
        .new({"partner": partner})
        ._get(id)
    )
    cart = env["sale.order"]._find_open_cart(partner.id)
    sale_line._action_reject_request(cart, data.reason)
    return RequestedSaleLine.from_sale_order_line(sale_line)


@unit_request_line_router.post("/unit/request_lines/{id}/reset")
async def reset_requested_sale_line(
    id: int,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_manager)],
) -> RequestedSaleLine:
    """
    Reset a specific requested sale line
    """
    sale_line = (
        env["shopinvader_api_unit_request.lines.helper"]
        .new({"partner": partner})
        ._get(id)
    )
    sale_line._action_reset_request()
    return RequestedSaleLine.from_sale_order_line(sale_line)


class ShopinvaderApiUnitCartSaleLineRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_unit_request.lines.helper"
    _description = "Shopinvader Api Unit Cart Sale Line Service Helper"

    partner = fields.Many2one("res.partner")

    def _get_domain_adapter(self):
        return [
            ("order_id.typology", "=", "request"),
            (
                "request_partner_id",
                "in",
                self.partner._get_unit()._get_unit_collaborators().ids,
            ),
            ("request_order_id", "=", False),
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
