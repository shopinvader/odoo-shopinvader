# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import Depends

from odoo import Command, models
from odoo.api import Environment
from odoo.exceptions import MissingError

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from odoo.addons.sale.models.sale_order import SaleOrder

from .schemas.sale import (
    QuotationAddLineRequest,
    QuotationCreateRequest,
    QuotationDeleteLineRequest,
    QuotationLines,
    QuotationUpdateInput,
    QuotationUpdateLineRequest,
)


class ShopinvaderApiQuotationRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_quotation.router.helper"
    _description = "Shopinvader api quotations router helper"
    _inherit = "shopinvader_api_sale.sales_router.helper"

    def _get_domain_adapter(self):
        return [
            ("partner_id", "=", self.partner.id),
            ("typology", "=", "quote"),
        ]

    def _process_confirm_quotation(self, quotation, data):
        """Process the quotation confirmation
        Can be inherited if you expect specific params
        for confirming a quotation"""
        return quotation.action_confirm_quotation()

    def _confirm(self, quotation_id, data) -> SaleOrder:
        quotation = self._get(quotation_id)
        self._process_confirm_quotation(quotation, data)
        return quotation

    def _update(self, quotation_id, data: QuotationUpdateInput) -> SaleOrder:
        quotation = self._get(quotation_id)
        vals = {"client_order_ref": data.client_order_ref}
        vals = self._modify_lines_vals(quotation, data.lines, vals)

        # remove any line that is in the quotation but does not appear in the request data
        request_line_ids = {
            line.line_id for line in data.lines if getattr(line, "line_id", None)
        }
        lines_to_remove_ids = [
            line.id for line in quotation.order_line if line.id not in request_line_ids
        ]
        for line_id in lines_to_remove_ids:
            vals["order_line"].append(Command.unlink(line_id))

        quotation.write(vals)
        return quotation

    def _create(self, rqst: QuotationCreateRequest) -> SaleOrder:
        vals = rqst.model_dump()
        vals["partner_id"] = self.partner.id

        # Enforce quote typology, correcting changes from other addons.
        vals["typology"] = "quote"

        if "lines" in vals:
            vals["order_line"] = [
                Command.create(
                    {
                        "product_id": line["product_id"],
                        "product_uom_qty": line["quantity"],
                    }
                )
                # use "pop" so that "lines" does not stay in "vals"
                # preventing an error in the "create" below
                for line in vals.pop("lines")
            ]

        quotation = self.env["sale.order"].create(vals)

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
        quotation = self._get(quotation_id)
        vals = self._modify_lines_vals(quotation, rqst.lines, {})
        quotation.write(vals)
        return quotation

    def _update_lines(
        self, quotation_id: int, rqst: QuotationLines[QuotationUpdateLineRequest]
    ) -> SaleOrder:
        quotation = self._get(quotation_id)
        vals = self._modify_lines_vals(quotation, rqst.lines, {})
        quotation.write(vals)
        return quotation

    def _delete_lines(
        self, quotation_id: int, rqst: QuotationLines[QuotationDeleteLineRequest]
    ) -> SaleOrder:
        quotation = self._get(quotation_id)
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


def quotation_router_helper(
    env: Annotated[Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> ShopinvaderApiQuotationRouterHelper:
    return env["shopinvader_api_quotation.router.helper"].new({"partner": partner})
