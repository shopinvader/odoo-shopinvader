# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import Depends, HTTPException, status

from odoo import Command, models
from odoo.api import Environment
from odoo.exceptions import MissingError

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from odoo.addons.sale.models.sale_order import SaleOrder
from odoo.addons.sale_quotation.exceptions import InvalidQuotationStateError

from .schemas import (
    QuotationAddLineRequest,
    QuotationCreateRequest,
    QuotationDeleteLineRequest,
    QuotationLines,
    QuotationUpdateInput,
    QuotationUpdateLineRequest,
)


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


class ShopinvaderApiQuotationRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_quotation.router.helper"
    _description = "Shopinvader api quotations router helper"
    _inherit = "shopinvader_api_sale.sales_router.helper"

    def _get_domain_adapter(self):
        return [
            ("partner_id", "=", self.partner.id),
            ("typology", "=", "quote"),
        ]

    def _process_unlink(self, quotation):
        """Process the unlink action on a quotation.
        Can be inherited if you expect specific params
        for deleting a quotation."""
        quotation.unlink()

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
        return quotation.action_customer_request_quotation()

    def _process_reset_to_draft(self, quotation):
        """Process the reset to draft action on a quotation.
        Can be inherited if you expect specific params
        for resetting a quotation to draft."""
        return quotation.action_customer_reset_quotation_to_draft()

    def _process_cancel(self, quotation):
        """Process the cancel action on a quotation.
        Can be inherited if you expect specific params
        for cancelling a quotation."""
        return quotation.action_customer_cancel_quotation()

    @InvalidQuotationStateErrorWrapper
    def _accept(self, quotation_id, data) -> SaleOrder:
        quotation = self._get(quotation_id)
        self._process_accept_quotation(quotation, data)
        return quotation

    def _delete(self, quotation_id: int) -> None:
        quotation = self._get(quotation_id)
        if quotation.quotation_state != "draft":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Quotation {quotation.id} cannot be deleted, "
                f"it is not in draft state.",
            )
        self._process_unlink(quotation)

    @InvalidQuotationStateErrorWrapper
    def _request_quotation(self, quotation_id: int) -> SaleOrder:
        quotation = self._get(quotation_id)
        self._process_request_quotation(quotation)
        return quotation

    @InvalidQuotationStateErrorWrapper
    def _reset_to_draft(self, quotation_id: int) -> SaleOrder:
        quotation = self._get(quotation_id)
        self._process_reset_to_draft(quotation)
        return quotation

    @InvalidQuotationStateErrorWrapper
    def _cancel(self, quotation_id: int) -> SaleOrder:
        quotation = self._get(quotation_id)
        self._process_cancel(quotation)
        return quotation

    def _ensure_can_update(self, quotation: SaleOrder):
        """Ensure that the quotation can be updated."""
        if quotation.quotation_state != "draft":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Quotation {quotation.id} cannot be updated, "
                f"it is not in draft state.",
            )

    def _update(self, quotation_id, data: QuotationUpdateInput) -> SaleOrder:
        quotation = self._get(quotation_id)
        self._ensure_can_update(quotation)
        vals = self._quotation_update_to_vals(quotation, data)
        if vals:
            quotation.write(vals)
        return quotation

    def _create(self, rqst: QuotationCreateRequest) -> SaleOrder:
        vals = self._quotation_create_to_vals(rqst)
        quotation = self.env["sale.order"].create(vals)

        # We need to add the `user_id` as follower manually because of
        # the way `MailThread._message_auto_subscribe_followers` works.
        # This function only assigns the `user_id` as a follower if given
        # explicitly inside the create dict (most likely a bug)
        quotation.message_subscribe(partner_ids=quotation.user_id.sudo().partner_id.ids)

        return quotation

    def _quotation_create_to_vals(self, data: QuotationCreateRequest) -> dict:
        vals = {"use_customer_quotation_workflow": True, "partner_id": self.partner.id}
        values = data.model_dump(exclude_unset=True)
        if "client_order_ref" in values:
            vals["client_order_ref"] = data.client_order_ref
        if "note" in values:
            vals["note"] = data.note
        if "lines" in values:
            vals["order_line"] = [
                Command.create(
                    {
                        "product_id": line.product_id,
                        "product_uom_qty": line.quantity,
                    }
                )
                for line in data.lines
            ]
        return vals

    def _quotation_update_to_vals(
        self, quotation: SaleOrder, data: QuotationUpdateInput
    ) -> dict:
        vals = {}
        values = data.model_dump(exclude_unset=True)
        if "client_order_ref" in values:
            vals["client_order_ref"] = data.client_order_ref
        if "note" in values:
            vals["note"] = data.note

        if "lines" in values:
            vals = self._modify_lines_vals(quotation, data.lines, vals)

            # remove any line that is in the quotation but does not appear in the request data
            request_line_ids = {
                line.line_id for line in data.lines if getattr(line, "line_id", None)
            }
            lines_to_remove_ids = [
                line.id
                for line in quotation.order_line
                if line.id not in request_line_ids
            ]
            for line_id in lines_to_remove_ids:
                vals["order_line"].append(Command.unlink(line_id))
        return vals

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
        quotation = self._get(quotation_id)
        self._ensure_can_update(quotation)
        vals = self._modify_lines_vals(quotation, rqst.lines, {})
        quotation.write(vals)
        return quotation

    def _update_lines(
        self, quotation_id: int, rqst: QuotationLines[QuotationUpdateLineRequest]
    ) -> SaleOrder:
        quotation = self._get(quotation_id)
        self._ensure_can_update(quotation)
        vals = self._modify_lines_vals(quotation, rqst.lines, {})
        quotation.write(vals)
        return quotation

    def _delete_lines(
        self, quotation_id: int, rqst: QuotationLines[QuotationDeleteLineRequest]
    ) -> SaleOrder:
        quotation = self._get(quotation_id)
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
        quotation.write(vals)
        return quotation

    def _get_pdf(self, record_id) -> tuple[str, bytes]:
        quotation = self._get(record_id)
        if quotation.quotation_state not in (
            "cancel",
            "waiting_acceptation",
            "accepted",
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Quotation cannot be downloaded before it is confirmed.",
            )
        return super()._get_pdf(record_id)


def quotation_router_helper(
    env: Annotated[Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> ShopinvaderApiQuotationRouterHelper:
    return env["shopinvader_api_quotation.router.helper"].new({"partner": partner})
