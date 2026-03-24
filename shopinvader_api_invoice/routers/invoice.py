# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
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
from odoo.addons.shopinvader_schema_invoice.schemas import Invoice, InvoiceSearch

invoice_router = APIRouter(tags=["invoices"])


class InvoiceHelper(VirtualModel):
    _inherit = "shopinvader.router.helper"
    _name = "shopinvader_api_invoice.invoices_router.helper"
    _description = "Shopinvader Api Invoice Service Helper"

    _model = "account.move"

    partner = fields.Many2one("res.partner", required=True)

    def _domain(self):
        return [
            ("partner_id", "=", self.partner.id),
            ("move_type", "in", ("out_invoice", "out_refund")),
            ("state", "not in", ("cancel", "draft")),
        ]

    def _get_pdf(self, record_id) -> tuple[str, bytes]:
        record = self._get(record_id)
        return record.sudo()._generate_report("account.account_invoices")


def invoice_helper(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
):
    return env["shopinvader_api_invoice.invoices_router.helper"].new(
        {"partner": partner}
    )


@invoice_router.get("/invoices")
def search(
    params: Annotated[InvoiceSearch, Depends()],
    helper: Annotated[InvoiceHelper, Depends(invoice_helper)],
    paging: Annotated[Paging, Depends(paging)],
) -> PagedCollection[Invoice]:
    """Get the list of current partner's invoices"""
    count, invoices = helper.search_with_count(
        params.to_odoo_domain(helper.env),
        limit=paging.limit,
        offset=paging.offset,
    )
    return PagedCollection[Invoice](
        count=count,
        items=[Invoice.from_account_move(invoice) for invoice in invoices],
    )


@invoice_router.get("/invoices/{invoice_id}")
def get(
    invoice_id: int,
    helper: Annotated[InvoiceHelper, Depends(invoice_helper)],
) -> Invoice:
    """
    Get the invoice of authenticated user with specific invoice_id
    """
    return Invoice.from_account_move(helper.get(invoice_id))


@invoice_router.get("/invoices/{invoice_id}/download")
def download(
    invoice_id: int,
    helper: Annotated[InvoiceHelper, Depends(invoice_helper)],
) -> FileResponse:
    """Download document."""
    filename, data = helper.generate_report(invoice_id, "account.account_invoices")
    return helper.send_file(filename, data, "application/pdf")
