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

    def _confirm(self, quotation_id, data):
        quotation = self._get(quotation_id)
        self._process_confirm_quotation(quotation, data)
        return quotation

    def _update(self, quotation_id, data):
        quotation = self._get(quotation_id)
        quotation.write(data.to_sale_order_vals())
        return quotation

    def _create(self, rqst: QuotationCreateRequest) -> SaleOrder:
        vals = rqst.model_dump()
        vals["partner_id"] = self.partner.id

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

    def _add_lines(
        self, quotation_id: int, rqst: QuotationLines[QuotationAddLineRequest]
    ) -> SaleOrder:
        quotation = self._get(quotation_id)
        for line in rqst.lines:
            quotation.write(
                {
                    "order_line": [
                        Command.create(
                            {
                                "product_id": line.product_id,
                                "product_uom_qty": line.quantity,
                            }
                        )
                    ]
                }
            )
        return quotation

    def _update_lines(
        self, quotation_id: int, rqst: QuotationLines[QuotationUpdateLineRequest]
    ) -> SaleOrder:
        quotation = self._get(quotation_id)
        existing_lines_ids = {line.id for line in quotation.order_line}
        vals = {"order_line": []}
        for update_line_rqst in rqst.lines:
            if update_line_rqst.line_id not in existing_lines_ids:
                raise MissingError(
                    f"Line with ID {update_line_rqst.line_id} "
                    f"not found in quotation {quotation_id}"
                )
            vals["order_line"].append(
                Command.update(
                    update_line_rqst.line_id,
                    {
                        "product_id": update_line_rqst.product_id,
                        "product_uom_qty": update_line_rqst.quantity,
                        "sequence": update_line_rqst.sequence,
                    },
                )
            )
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
                    f"not found in quotation {quotation_id}"
                )
            vals["order_line"].append(Command.delete(delete_line_rqst.line_id))
        quotation.write(vals)
        return quotation


def quotation_router_helper(
    env: Annotated[Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> ShopinvaderApiQuotationRouterHelper:
    return env["shopinvader_api_quotation.router.helper"].new({"partner": partner})
