from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, StreamingResponse

from odoo.http import content_disposition

from odoo.addons.extendable_fastapi.schemas import PagedCollection
from odoo.addons.fastapi.dependencies import paging
from odoo.addons.fastapi.schemas import Paging
from odoo.addons.shopinvader_schema_sale.schemas.sale import Sale, SaleSearch

from ..dependencies import ShopinvaderApiQuotationRouterHelper, quotation_router_helper
from ..schemas.sale import (
    QuotationAddLineRequest,
    QuotationConfirmInput,
    QuotationCreateRequest,
    QuotationDeleteLineRequest,
    QuotationLines,
    QuotationUpdateInput,
    QuotationUpdateLineRequest,
)

quotation_router = APIRouter(tags=["quotations"])


@quotation_router.post("/quotations/create", status_code=201)
def create_quotation(
    quotation_router_helper: Annotated[
        ShopinvaderApiQuotationRouterHelper, Depends(quotation_router_helper)
    ],
    rqst: QuotationCreateRequest,
) -> Sale:
    quotation = quotation_router_helper._create(rqst)
    return Sale.from_sale_order(quotation)


@quotation_router.get("/quotations/{quotation_id}")
def get(
    quotation_router_helper: Annotated[
        ShopinvaderApiQuotationRouterHelper, Depends(quotation_router_helper)
    ],
    quotation_id: int,
) -> Sale | None:
    quotation = quotation_router_helper._get(quotation_id)
    return Sale.from_sale_order(quotation)


@quotation_router.get("/quotations", status_code=200)
def search_quotation(
    params: Annotated[SaleSearch, Depends()],
    paging: Annotated[Paging, Depends(paging)],
    quotation_router_helper: Annotated[
        ShopinvaderApiQuotationRouterHelper, Depends(quotation_router_helper)
    ],
) -> PagedCollection[Sale]:
    count, orders = quotation_router_helper._search(paging, params)
    return PagedCollection[Sale](
        count=count,
        items=[Sale.from_sale_order(order) for order in orders],
    )


@quotation_router.post("/quotations/{quotation_id}")
def update_quotation(
    data: QuotationUpdateInput,
    quotation_router_helper: Annotated[
        ShopinvaderApiQuotationRouterHelper, Depends(quotation_router_helper)
    ],
    quotation_id: int,
) -> Sale:
    order = quotation_router_helper._update(quotation_id, data)
    return Sale.from_sale_order(order)


@quotation_router.get("/quotations/{quotation_id}/download")
def download(
    quotation_id: int,
    quotation_router_helper: Annotated[
        ShopinvaderApiQuotationRouterHelper, Depends(quotation_router_helper)
    ],
) -> FileResponse:
    """Download document."""
    filename, pdf = quotation_router_helper._get_pdf(quotation_id)
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


@quotation_router.post("/quotations/{quotation_id}/add_line", status_code=201)
def add_line(
    quotation_router_helper: Annotated[
        ShopinvaderApiQuotationRouterHelper, Depends(quotation_router_helper)
    ],
    quotation_id: int,
    rqst: QuotationAddLineRequest,
) -> Sale:
    quotation = quotation_router_helper._add_lines(
        quotation_id, QuotationLines[QuotationAddLineRequest](lines=[rqst])
    )
    return Sale.from_sale_order(quotation)


@quotation_router.post("/quotations/{quotation_id}/add_lines", status_code=201)
def add_lines(
    quotation_router_helper: Annotated[
        ShopinvaderApiQuotationRouterHelper, Depends(quotation_router_helper)
    ],
    quotation_id: int,
    rqst: QuotationLines[QuotationAddLineRequest],
) -> Sale:
    quotation = quotation_router_helper._add_lines(quotation_id, rqst)
    return Sale.from_sale_order(quotation)


@quotation_router.put("/quotations/{quotation_id}/update_line", status_code=200)
def update_line(
    quotation_router_helper: Annotated[
        ShopinvaderApiQuotationRouterHelper, Depends(quotation_router_helper)
    ],
    quotation_id: int,
    rqst: QuotationUpdateLineRequest,
) -> Sale:
    quotation = quotation_router_helper._update_lines(
        quotation_id, QuotationLines[QuotationUpdateLineRequest](lines=[rqst])
    )
    return Sale.from_sale_order(quotation)


@quotation_router.put("/quotations/{quotation_id}/update_lines", status_code=200)
def update_lines(
    quotation_router_helper: Annotated[
        ShopinvaderApiQuotationRouterHelper, Depends(quotation_router_helper)
    ],
    quotation_id: int,
    rqst: QuotationLines[QuotationUpdateLineRequest],
) -> Sale:
    quotation = quotation_router_helper._update_lines(quotation_id, rqst)
    return Sale.from_sale_order(quotation)


@quotation_router.post("/quotations/{quotation_id}/delete_line", status_code=200)
def delete_line(
    quotation_router_helper: Annotated[
        ShopinvaderApiQuotationRouterHelper, Depends(quotation_router_helper)
    ],
    quotation_id: int,
    rqst: QuotationDeleteLineRequest,
) -> Sale:
    quotation = quotation_router_helper._delete_lines(
        quotation_id, QuotationLines[QuotationDeleteLineRequest](lines=[rqst])
    )
    return Sale.from_sale_order(quotation)


@quotation_router.post("/quotations/{quotation_id}/delete_lines", status_code=200)
def delete_lines(
    quotation_router_helper: Annotated[
        ShopinvaderApiQuotationRouterHelper, Depends(quotation_router_helper)
    ],
    quotation_id: int,
    rqst: QuotationLines[QuotationDeleteLineRequest],
) -> Sale:
    quotation = quotation_router_helper._delete_lines(quotation_id, rqst)
    return Sale.from_sale_order(quotation)


@quotation_router.delete("/quotations/{quotation_id}", status_code=200)
def delete_quotation(
    quotation_router_helper: Annotated[
        ShopinvaderApiQuotationRouterHelper, Depends(quotation_router_helper)
    ],
    quotation_id: int,
) -> None:
    """Delete a quotation."""
    quotation_router_helper._delete(quotation_id)
    return None


# Workflow related methods


@quotation_router.post("/quotations/{quotation_id}/request_quotation", status_code=200)
def request_quotation(
    quotation_router_helper: Annotated[
        ShopinvaderApiQuotationRouterHelper, Depends(quotation_router_helper)
    ],
    quotation_id: int,
) -> Sale:
    """Request a quotation by the Saler."""
    quotation = quotation_router_helper._request_quotation(quotation_id)
    return Sale.from_sale_order(quotation)


@quotation_router.post("/quotations/{quotation_id}/reset_to_draft", status_code=200)
def reset_to_draft(
    quotation_router_helper: Annotated[
        ShopinvaderApiQuotationRouterHelper, Depends(quotation_router_helper)
    ],
    quotation_id: int,
) -> Sale:
    """Reset a quotation to draft state."""
    quotation = quotation_router_helper._reset_to_draft(quotation_id)
    return Sale.from_sale_order(quotation)


@quotation_router.post("/quotations/{quotation_id}/accept", status_code=200)
def accept_quotation(
    quotation_router_helper: Annotated[
        ShopinvaderApiQuotationRouterHelper, Depends(quotation_router_helper)
    ],
    quotation_id: int,
    data: QuotationConfirmInput | None = None,
) -> Sale:
    """Accept a quotation."""
    order = quotation_router_helper._accept(quotation_id, data)
    return Sale.from_sale_order(order)


@quotation_router.post("/quotations/{quotation_id}/cancel", status_code=200)
def cancel_quotation(
    quotation_router_helper: Annotated[
        ShopinvaderApiQuotationRouterHelper, Depends(quotation_router_helper)
    ],
    quotation_id: int,
) -> Sale:
    """Cancel a quotation."""
    quotation = quotation_router_helper._cancel(quotation_id)
    return Sale.from_sale_order(quotation)
