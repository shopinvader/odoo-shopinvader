# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import api, fields

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.extendable_fastapi.schemas import PagedCollection
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
    paging,
)
from odoo.addons.fastapi.schemas import Paging
from odoo.addons.shopinvader_router_helper import VirtualModel

from ..schemas import SaleLineSearch, SaleLineWithSale

sale_line_router = APIRouter(tags=["sales"])


class SaleLineHelper(VirtualModel):
    _inherit = "shopinvader.router.helper"
    _name = "shopinvader_api_sale.sale_line_router.helper"
    _description = "Shopinvader Api Sale Line Service Helper"

    _model = "sale.order.line"

    partner = fields.Many2one("res.partner")

    def _domain(self):
        return [
            ("order_id.partner_id", "=", self.partner.id),
            ("order_id.typology", "=", "sale"),
        ]


def sale_line_helper(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
):
    return env["shopinvader_api_sale.sale_line_router.helper"].new({"partner": partner})


@sale_line_router.get("/sales/lines")
@sale_line_router.get("/sales/{sale_id}/lines")
def search(
    params: Annotated[SaleLineSearch, Depends()],
    paging: Annotated[Paging, Depends(paging)],
    helper: Annotated[SaleLineHelper, Depends(sale_line_helper)],
    sale_id: int | None = None,
) -> PagedCollection[SaleLineWithSale]:
    """Get / search sale order lines. The list contains only sale order lines from the
    authenticated user"""
    if sale_id:
        # Shortcut to search by sale_id
        params.order_id = sale_id

    count, sols = helper.search_with_count(
        params.to_odoo_domain(helper.env),
        limit=paging.limit,
        offset=paging.offset,
    )
    return PagedCollection[SaleLineWithSale](
        count=count,
        items=[SaleLineWithSale.from_sale_order_line(sol) for sol in sols],
    )


@sale_line_router.get("/sales/lines/{sale_line_id}")
def get(
    sale_line_id: int,
    helper: Annotated[SaleLineHelper, Depends(sale_line_helper)],
) -> SaleLineWithSale:
    """
    Get sale order of authenticated user with specific sale_id
    """
    return SaleLineWithSale.from_sale_order_line(helper.get(sale_line_id))
