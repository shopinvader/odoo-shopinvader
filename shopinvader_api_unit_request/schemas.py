# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import Annotated

from extendable_pydantic import StrictExtendableBaseModel
from pydantic import Field

from odoo import api

from odoo.addons.shopinvader_api_sale.schemas import SaleLineWithSale


class RejectRequest(StrictExtendableBaseModel, extra="ignore"):
    reason: str | None = None


class RequestedSaleLine(SaleLineWithSale):
    partner_id: int
    request_rejected: bool
    request_rejection_reason: str | None = None

    @classmethod
    def from_sale_order_line(cls, odoo_rec):
        res = super().from_sale_order_line(odoo_rec)
        res.partner_id = odoo_rec.request_partner_id.id
        res.request_rejected = odoo_rec.request_rejected
        res.request_rejection_reason = odoo_rec.request_rejection_reason or None
        return res


class RequestedSaleLineSearch(StrictExtendableBaseModel, extra="ignore"):
    order_name: Annotated[
        str | None,
        Field(
            description="When used, the search look for any sale order lines "  # noqa
            "where the order name contains the given value case insensitively."  # noqa
        ),
    ] = None
    product_name: Annotated[
        str | None,
        Field(
            description="When used, the search look for any sale order lines "  # noqa
            "where the product name contains the given value case insensitively."  # noqa
        ),
    ] = None
    rejected: Annotated[
        bool | None,
        Field(
            description="When used, the search also includes the "  # noqa
            "rejected sale order lines."  # noqa
        ),
    ] = None

    def to_odoo_domain(self, env: api.Environment):
        domain = []
        if self.order_name:
            domain.append(("order_id.name", "ilike", self.order_name))

        if self.product_name:
            domain.append(("product_id.name", "ilike", self.product_name))

        if not self.rejected:
            domain.append(("request_rejected", "=", False))

        return domain
