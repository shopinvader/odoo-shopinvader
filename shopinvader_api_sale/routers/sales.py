# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

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
from odoo.addons.shopinvader_schema_sale.schemas import Sale, SaleSearch

sale_router = APIRouter(tags=["sales"])


class SaleHelper(VirtualModel):
    _inherit = "shopinvader.router.helper"
    _name = "shopinvader_api_sale.sales_router.helper"
    _description = "Shopinvader Api Sale Service Helper"
    _model = "sale.order"

    partner = fields.Many2one("res.partner", required=True)

    def _domain(self):
        return [
            ("partner_id", "=", self.partner.id),
            ("typology", "=", "sale"),
        ]


def sale_helper(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
):
    return env["shopinvader_api_sale.sales_router.helper"].new({"partner": partner})


@sale_router.get("/sales")
def search(
    params: Annotated[SaleSearch, Depends()],
    paging: Annotated[Paging, Depends(paging)],
    helper: Annotated[SaleHelper, Depends(sale_helper)],
) -> PagedCollection[Sale]:
    """Get / search sale orders. The list contains only sale orders from the
    authenticated user"""
    count, orders = helper.search_with_count(
        params.to_odoo_domain(helper.env),
        limit=paging.limit,
        offset=paging.offset,
    )
    return PagedCollection[Sale](
        count=count,
        items=[Sale.from_sale_order(order) for order in orders],
    )


@sale_router.get("/sales/{sale_id}")
def get(
    sale_id: int,
    helper: Annotated[SaleHelper, Depends(sale_helper)],
) -> Sale:
    """
    Get sale order of authenticated user with specific sale_id
    """
    return Sale.from_sale_order(helper.get(sale_id))


@sale_router.get("/sales/{sale_id}/download")
def download(
    sale_id: int,
    helper: Annotated[SaleHelper, Depends(sale_helper)],
) -> FileResponse:
    """Download document."""
    filename, data = helper.generate_report(sale_id, "sale.action_report_saleorder")
    return helper.send_file(filename, data, "application/pdf")
