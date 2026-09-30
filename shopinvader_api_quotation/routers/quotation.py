# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections.abc import Callable
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from odoo import Command, api, models
from odoo.exceptions import MissingError
from odoo.http import content_disposition

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.extendable_fastapi.schemas import PagedCollection
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
    paging,
)
from odoo.addons.fastapi.schemas import Paging
from odoo.addons.sale.models.sale_order import SaleOrder
from odoo.addons.sale_quotation.exceptions import InvalidQuotationStateError
from odoo.addons.shopinvader_router_helper import VirtualModel
from odoo.addons.shopinvader_schema_sale.schemas.sale import Sale

from ..schemas import (
    QuotationAddLineRequest,
    QuotationConfirmInput,
    QuotationCreateRequest,
    QuotationDeleteLineRequest,
    QuotationLines,
    QuotationSearch,
    QuotationUpdateInput,
    QuotationUpdateLineRequest,
)

quotation_router = APIRouter(tags=["quotations"])


def InvalidQuotationStateErrorWrapper(func):
    """Decorator to wrap methods that may raise a conflict error."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except InvalidQuotationStateError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            ) from e

    return wrapper


class QuotationHelper(VirtualModel):
    _inherit = "shopinvader_api_sale.sales_router.helper"
    _name = "shopinvader_api_quotation.quotations_router.helper"
    _description = "Shopinvader api quotation router helper"
    _model = "sale.order"

    def _domain(self):
        return [
            ("partner_id", "=", self.partner.id),
            ("typology", "=", "quote"),
        ]

    def _process_confirm_quotation(self, quotation, data):
        """Process the quotation confirmation
        Can be inherited if you expect specific params
        for confirming a quotation"""
        return quotation.action_confirm_quotation()

    def _ensure_can_update(self, quotation: SaleOrder):
        """Ensure that the quotation can be updated."""
        if quotation.quotation_state != "draft":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Quotation {quotation.id} cannot be updated, "
                f"it is not in draft state.",
            )
        self.model.check_access("write")

    def _prepare_values(self, values: Any) -> dict:
        values = super()._prepare_values(values)
        vals = {}
        data = values.model_dump(exclude_unset=True)
        if "client_order_ref" in data:
            vals["client_order_ref"] = values.client_order_ref
        if "note" in data:
            vals["note"] = values.note
        return vals

    def _prepare_create_values(self, values: Any) -> dict:
        vals = super()._prepare_create_values(values)
        vals = {
            "use_customer_quotation_workflow": True,
            "partner_id": self.partner.id,
            **vals,
        }

        data = values.model_dump(exclude_unset=True)
        if "lines" in data:
            vals["order_line"] = [
                Command.create(
                    {
                        "product_id": line.product_id,
                        "product_uom_qty": line.quantity,
                    }
                )
                for line in values.lines
            ]
        return vals

    def _prepare_write_values(self, values: Any, record: SaleOrder) -> dict:
        vals = super()._prepare_write_values(values, record)

        data = values.model_dump(exclude_unset=True)
        if "lines" in data:
            vals = self._modify_lines_vals(record, values.lines, vals)

            # remove any line that is in the quotation but does not appear in the request data
            request_line_ids = {
                line.line_id for line in values.lines if getattr(line, "line_id", None)
            }
            lines_to_remove_ids = [
                line.id for line in record.order_line if line.id not in request_line_ids
            ]
            for line_id in lines_to_remove_ids:
                vals["order_line"].append(Command.unlink(line_id))
        return vals

    def create(self, values: Any) -> SaleOrder:
        quotation = super().create(values)

        # We need to add the `user_id` as follower manually because of
        # the way `MailThread._message_auto_subscribe_followers` works.
        # This function only assigns the `user_id` as a follower if given
        # explicitly inside the create dict (most likely a bug)
        quotation.sudo().message_subscribe(
            partner_ids=quotation.user_id.sudo().partner_id.ids
        )

        return quotation

    def write(self, record_id: int, values: dict) -> SaleOrder:
        record = self.get(record_id)
        self._ensure_can_update(record)
        return super().write(record_id, values)

    def unlink(
        self, record_id: int, deletion_info_callback: Callable | None = None
    ) -> None:
        record = self.get(record_id)
        if record.quotation_state != "draft":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Quotation {record.id} cannot be deleted, "
                f"it is not in draft state.",
            )
        return super().unlink(record_id, deletion_info_callback)

    def _process_accept_quotation(self, quotation, data):
        """Process the quotation acceptation
        Can be inherited if you expect specific params
        for confirming a quotation"""
        # Elevate context to sudo() so the background procurement generation
        # triggered by sale_stock can bypass portal/public user ACL limits.
        return quotation.sudo().action_customer_accept_quotation()

    def _process_request_quotation(self, quotation):
        """Process the quotation request
        Can be inherited if you expect specific params
        for requesting a quotation"""
        return quotation.sudo().action_customer_request_quotation()

    def _process_reset_to_draft(self, quotation):
        """Process the reset to draft action on a quotation.
        Can be inherited if you expect specific params
        for resetting a quotation to draft."""
        return quotation.sudo().action_customer_reset_quotation_to_draft()

    def _process_cancel(self, quotation):
        """Process the cancel action on a quotation.
        Can be inherited if you expect specific params
        for cancelling a quotation."""
        return quotation.sudo().action_customer_cancel_quotation()

    @InvalidQuotationStateErrorWrapper
    def _accept(self, quotation_id, data) -> SaleOrder:
        quotation = self.get(quotation_id)
        self._process_accept_quotation(quotation, data)
        return quotation

    @InvalidQuotationStateErrorWrapper
    def _request_quotation(self, quotation_id: int) -> SaleOrder:
        quotation = self.get(quotation_id)
        self._process_request_quotation(quotation)
        return quotation

    @InvalidQuotationStateErrorWrapper
    def _reset_to_draft(self, quotation_id: int) -> SaleOrder:
        quotation = self.get(quotation_id)
        self._process_reset_to_draft(quotation)
        return quotation

    @InvalidQuotationStateErrorWrapper
    def _cancel(self, quotation_id: int) -> SaleOrder:
        quotation = self.get(quotation_id)
        self._process_cancel(quotation)
        return quotation

    def _modify_lines_vals(
        self,
        quotation: SaleOrder,
        lines: QuotationLines[QuotationAddLineRequest | QuotationUpdateLineRequest],
        vals: dict,
    ):
        """
        Prepares 'order_line' commands for sale order updates.

        Modifies the `vals` dictionary in-place to include `order_line` commands.
        """
        vals["order_line"] = []
        existing_lines_ids = {line.id for line in quotation.order_line}

        # If given a line_id, update this line, otherwiser, create a new line.
        for line in lines:
            if getattr(line, "line_id", None):
                if line.line_id not in existing_lines_ids:
                    raise MissingError(
                        f"Line with ID {line.line_id} "
                        f"not found inside quotation {quotation.id}"
                    )
                vals["order_line"].append(
                    Command.update(
                        line.line_id,
                        {
                            "product_id": line.product_id,
                            "product_uom_qty": line.quantity,
                            "sequence": line.sequence,
                        },
                    )
                )
            else:
                vals["order_line"].append(
                    Command.create(
                        {
                            "product_id": line.product_id,
                            "product_uom_qty": line.quantity,
                            "sequence": line.sequence,
                        },
                    )
                )

        return vals

    def _add_lines(
        self, quotation_id: int, rqst: QuotationLines[QuotationAddLineRequest]
    ) -> SaleOrder:
        quotation = self.get(quotation_id)
        self._ensure_can_update(quotation)
        vals = self._modify_lines_vals(quotation, rqst.lines, {})
        quotation.sudo().write(vals)
        return quotation

    def _update_lines(
        self, quotation_id: int, rqst: QuotationLines[QuotationUpdateLineRequest]
    ) -> SaleOrder:
        quotation = self.get(quotation_id)
        self._ensure_can_update(quotation)
        vals = self._modify_lines_vals(quotation, rqst.lines, {})
        quotation.sudo().write(vals)
        return quotation

    def _delete_lines(
        self, quotation_id: int, rqst: QuotationLines[QuotationDeleteLineRequest]
    ) -> SaleOrder:
        quotation = self.get(quotation_id)
        self._ensure_can_update(quotation)
        existing_lines_ids = {line.id for line in quotation.order_line}
        vals = {"order_line": []}
        for delete_line_rqst in rqst.lines:
            if delete_line_rqst.line_id not in existing_lines_ids:
                raise MissingError(
                    f"Line with ID {delete_line_rqst.line_id} "
                    f"not found inside quotation {quotation_id}"
                )
            vals["order_line"].append(Command.delete(delete_line_rqst.line_id))
        quotation.sudo().write(vals)
        return quotation

    def generate_report(self, record_id: int, report_name: str) -> tuple[str, bytes]:
        quotation = self.get(record_id)
        if quotation.quotation_state not in (
            "cancel",
            "waiting_acceptation",
            "accepted",
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Quotation cannot be downloaded before it is confirmed.",
            )
        return super().generate_report(record_id, report_name)


def quotation_helper(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
):
    return env["shopinvader_api_quotation.quotations_router.helper"].new(
        {"partner": partner}
    )


@quotation_router.post("/quotations/create", status_code=201)
def create_quotation(
    helper: Annotated[QuotationHelper, Depends(quotation_helper)],
    rqst: QuotationCreateRequest,
) -> Sale:
    return Sale.from_sale_order(helper.create(rqst))


@quotation_router.get("/quotations/{quotation_id}")
def get(
    helper: Annotated[QuotationHelper, Depends(quotation_helper)],
    quotation_id: int,
) -> Sale | None:
    return Sale.from_sale_order(helper.get(quotation_id))


@quotation_router.get("/quotations", status_code=200)
def search_quotation(
    params: Annotated[QuotationSearch, Depends()],
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


@quotation_router.post("/quotations/{quotation_id}/add_line", status_code=201)
def add_line(
    helper: Annotated[QuotationHelper, Depends(quotation_helper)],
    quotation_id: int,
    rqst: QuotationAddLineRequest,
) -> Sale:
    quotation = helper._add_lines(
        quotation_id, QuotationLines[QuotationAddLineRequest](lines=[rqst])
    )
    return Sale.from_sale_order(quotation)


@quotation_router.post("/quotations/{quotation_id}/add_lines", status_code=201)
def add_lines(
    helper: Annotated[QuotationHelper, Depends(quotation_helper)],
    quotation_id: int,
    rqst: QuotationLines[QuotationAddLineRequest],
) -> Sale:
    quotation = helper._add_lines(quotation_id, rqst)
    return Sale.from_sale_order(quotation)


@quotation_router.put("/quotations/{quotation_id}/update_line", status_code=200)
def update_line(
    helper: Annotated[QuotationHelper, Depends(quotation_helper)],
    quotation_id: int,
    rqst: QuotationUpdateLineRequest,
) -> Sale:
    quotation = helper._update_lines(
        quotation_id, QuotationLines[QuotationUpdateLineRequest](lines=[rqst])
    )
    return Sale.from_sale_order(quotation)


@quotation_router.put("/quotations/{quotation_id}/update_lines", status_code=200)
def update_lines(
    helper: Annotated[QuotationHelper, Depends(quotation_helper)],
    quotation_id: int,
    rqst: QuotationLines[QuotationUpdateLineRequest],
) -> Sale:
    quotation = helper._update_lines(quotation_id, rqst)
    return Sale.from_sale_order(quotation)


@quotation_router.post("/quotations/{quotation_id}/delete_line", status_code=200)
def delete_line(
    helper: Annotated[QuotationHelper, Depends(quotation_helper)],
    quotation_id: int,
    rqst: QuotationDeleteLineRequest,
) -> Sale:
    quotation = helper._delete_lines(
        quotation_id, QuotationLines[QuotationDeleteLineRequest](lines=[rqst])
    )
    return Sale.from_sale_order(quotation)


@quotation_router.post("/quotations/{quotation_id}/delete_lines", status_code=200)
def delete_lines(
    helper: Annotated[QuotationHelper, Depends(quotation_helper)],
    quotation_id: int,
    rqst: QuotationLines[QuotationDeleteLineRequest],
) -> Sale:
    quotation = helper._delete_lines(quotation_id, rqst)
    return Sale.from_sale_order(quotation)


@quotation_router.delete("/quotations/{quotation_id}", status_code=200)
def delete_quotation(
    helper: Annotated[QuotationHelper, Depends(quotation_helper)],
    quotation_id: int,
) -> None:
    """Delete a quotation."""
    return helper.unlink(
        quotation_id,
        lambda quotation: Sale.from_sale_order(quotation),
    )


# Workflow related methods


@quotation_router.post("/quotations/{quotation_id}/request_quotation", status_code=200)
def request_quotation(
    helper: Annotated[QuotationHelper, Depends(quotation_helper)],
    quotation_id: int,
) -> Sale:
    """Request a quotation by the Saler."""
    quotation = helper._request_quotation(quotation_id)
    return Sale.from_sale_order(quotation)


@quotation_router.post("/quotations/{quotation_id}/reset_to_draft", status_code=200)
def reset_to_draft(
    helper: Annotated[QuotationHelper, Depends(quotation_helper)],
    quotation_id: int,
) -> Sale:
    """Reset a quotation to draft state."""
    quotation = helper._reset_to_draft(quotation_id)
    return Sale.from_sale_order(quotation)


@quotation_router.post("/quotations/{quotation_id}/accept", status_code=200)
def accept_quotation(
    helper: Annotated[QuotationHelper, Depends(quotation_helper)],
    quotation_id: int,
    data: QuotationConfirmInput | None = None,
) -> Sale:
    """Accept a quotation."""
    order = helper._accept(quotation_id, data)
    return Sale.from_sale_order(order)


@quotation_router.post("/quotations/{quotation_id}/cancel", status_code=200)
def cancel_quotation(
    helper: Annotated[QuotationHelper, Depends(quotation_helper)],
    quotation_id: int,
) -> Sale:
    """Cancel a quotation."""
    quotation = helper._cancel(quotation_id)
    return Sale.from_sale_order(quotation)
