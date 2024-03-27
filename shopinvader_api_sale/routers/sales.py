# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, StreamingResponse

from odoo import api, fields, models
from odoo.http import content_disposition
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.extendable_fastapi.schemas import PagedCollection
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
    paging,
)
from odoo.addons.fastapi.schemas import Paging
from odoo.addons.sale.models.sale_order import SaleOrder
from odoo.addons.shopinvader_filtered_model.utils import FilteredModelAdapter
from odoo.addons.shopinvader_schema_sale.schemas import Sale, SaleSearch

sale_router = APIRouter(tags=["sales"])


@sale_router.get("/sales")
def search(
    params: Annotated[SaleSearch, Depends()],
    paging: Annotated[Paging, Depends(paging)],
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> PagedCollection[Sale]:
    """Get / search sale orders. The list contains only sale orders from the
    authenticated user"""
    count, orders = (
        env["shopinvader_api_sale.sales_router.helper"]
        .new({"partner": partner})
        ._search(paging, params)
    )
    return PagedCollection[Sale](
        count=count,
        items=[Sale.from_sale_order(order) for order in orders.sudo()],
    )


@sale_router.get("/sales/{sale_id}")
def get(
    sale_id: int,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> Sale:
    """
    Get sale order of authenticated user with specific sale_id
    """
    return Sale.from_sale_order(
        env["shopinvader_api_sale.sales_router.helper"]
        .new({"partner": partner})
        ._get(sale_id)
        .sudo()
    )


@sale_router.get("/sales/{sale_id}/download")
def download(
    sale_id: int,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> FileResponse:
    """Download document."""
    filename, pdf = (
        env["shopinvader_api_sale.sales_router.helper"]
        .new({"partner": partner})
        ._get_pdf(sale_id)
    )
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"
    header = {
        "Content-Disposition": content_disposition(filename),
    }

    def pseudo_stream():
        yield pdf

    return StreamingResponse(
        pseudo_stream(), headers=header, media_type="application/pdf"
    )


class ShopinvaderApiSaleSalesRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_sale.sales_router.helper"
    _description = "Shopinvader Api Sale Service Helper"

    partner = fields.Many2one("res.partner")

    def _get_domain_adapter(self):
        return [
            ("partner_id", "=", self.partner.id),
            ("typology", "=", "sale"),
        ]

    @property
    def model_adapter(self) -> FilteredModelAdapter[SaleOrder]:
        return FilteredModelAdapter[SaleOrder](self.env, self._get_domain_adapter())

    def _get(self, record_id) -> SaleOrder:
        return self.model_adapter.get(record_id)

    def _search(self, paging, params) -> tuple[int, SaleOrder]:
        return self.model_adapter.search_with_count(
            params.to_odoo_domain(self.env),
            limit=paging.limit,
            offset=paging.offset,
        )

    def _get_pdf(self, record_id) -> tuple[str, bytes]:
        record = self._get(record_id)
        report = self.env["ir.actions.report"]._get_report(
            "sale.action_report_saleorder"
        )
        filename = safe_eval(report.print_report_name, {"object": record})
        content = (
            self.env["ir.actions.report"]
            .sudo()
            ._render_qweb_pdf("sale.action_report_saleorder", [record.id])[0]
        )
        return filename, content
