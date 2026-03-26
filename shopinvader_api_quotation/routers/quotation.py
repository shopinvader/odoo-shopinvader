from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from odoo import api

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.extendable_fastapi.schemas import PagedCollection
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
    paging,
)
from odoo.addons.fastapi.schemas import Paging
from odoo.addons.shopinvader_router_helper import VirtualModel
from odoo.addons.shopinvader_schema_sale.schemas.sale import Sale, SaleSearch

from ..schemas.sale import QuotationConfirmInput, QuotationUpdateInput

# create a router
quotation_router = APIRouter(tags=["quotations"])


class QuotationHelper(VirtualModel):
    _inherit = "shopinvader_api_sale.sales_router.helper"
    _name = "shopinvader_api_quotation.quotations_router.helper"
    _description = "Shopinvader api quotation router helper"
    _model = "sale.order"

    def _domain(self):
        return [
            ("partner_id", "=", self.partner.id),
            ("quotation_state", "in", ("customer_request", "waiting_acceptation")),
        ]

    def _prepare_values(self, data):
        return data.to_sale_order_vals()

    def _process_confirm_quotation(self, quotation, data):
        """Process the quotation confirmation
        Can be inherited if you expect specific params
        for confirming a quotation"""
        return quotation.action_confirm_quotation()

    def _confirm(self, quotation_id, data):
        quotation = self.get(quotation_id)
        self._process_confirm_quotation(quotation, data)
        return quotation


def quotation_helper(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
):
    return env["shopinvader_api_quotation.quotations_router.helper"].new(
        {"partner": partner}
    )


@quotation_router.get("/quotations/{quotation_id}")
def get(
    helper: Annotated[QuotationHelper, Depends(quotation_helper)],
    quotation_id: int,
) -> Sale | None:
    return Sale.from_sale_order(helper.get(quotation_id))


@quotation_router.post("/quotations/{quotation_id}/confirm", status_code=200)
def confirm_quotation(
    quotation_id: int,
    helper: Annotated[QuotationHelper, Depends(quotation_helper)],
    data: QuotationConfirmInput | None = None,
) -> None:
    return Sale.from_sale_order(helper._confirm(quotation_id, data))


@quotation_router.get("/quotations", status_code=200)
def search_quotation(
    params: Annotated[SaleSearch, Depends()],
    paging: Annotated[Paging, Depends(paging)],
    helper: Annotated[QuotationHelper, Depends(quotation_helper)],
) -> PagedCollection[Sale]:
    count, orders = helper.search_with_count(
        params.to_odoo_domain(helper.env),
        limit=paging.limit,
        offset=paging.offset,
    )
    return PagedCollection[Sale](
        count=count,
        items=[Sale.from_sale_order(order) for order in orders],
    )


@quotation_router.post("/quotations/{quotation_id}")
def update_quotation(
    data: QuotationUpdateInput,
    quotation_id: int,
    helper: Annotated[QuotationHelper, Depends(quotation_helper)],
) -> Sale:
    return Sale.from_sale_order(helper.write(quotation_id, data))


@quotation_router.get("/quotations/{quotation_id}/download")
def download(
    quotation_id: int,
    helper: Annotated[QuotationHelper, Depends(quotation_helper)],
) -> FileResponse:
    """Download document."""
    filename, data = helper.generate_report(
        quotation_id, "sale.action_report_saleorder"
    )
    return helper.send_file(filename, data, "application/pdf")
