# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import Annotated

from extendable_pydantic import StrictExtendableBaseModel
from pydantic import Field

from odoo import api

from odoo.addons.shopinvader_api_sale import schemas


class RejectRequest(StrictExtendableBaseModel, extra="ignore"):
    reason: str | None = None


class SaleLineWithSale(schemas.SaleLineWithSale, extends=True):
    request_order_id: int | None
    request_partner_id: int | None
    request_rejected: bool
    request_rejection_reason: str | None = None

    @classmethod
    def from_sale_order_line(cls, odoo_rec):
        res = super().from_sale_order_line(odoo_rec)
        res.request_order_id = (
            odoo_rec.request_order_id.id if odoo_rec.request_order_id else None
        )
        res.request_partner_id = (
            odoo_rec.request_partner_id.id if odoo_rec.request_partner_id else None
        )
        res.request_rejected = odoo_rec.request_rejected
        res.request_rejection_reason = odoo_rec.request_rejection_reason or None
        return res


class RequestedSaleLine(SaleLineWithSale):
    partner_id: int

    @classmethod
    def from_sale_order_line(cls, odoo_rec):
        res = super().from_sale_order_line(odoo_rec)
        res.partner_id = odoo_rec.request_partner_id.id
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
    request_partner_name: Annotated[
        str | None,
        Field(
            description="When used, the search look for any sale order lines "  # noqa
            "where the request partner name contains the given value case insensitively."  # noqa
        ),
    ] = None
    sort_by: str | None = None

    def to_odoo_domain(self, env: api.Environment):
        domain = []
        if self.order_name:
            domain.append(("order_id.name", "ilike", self.order_name))

        if self.product_name:
            domain.append(("product_id.name", "ilike", self.product_name))

        if not self.rejected:
            domain.append(("request_rejected", "=", False))

        if self.request_partner_name:
            domain.append(
                ("request_partner_id.name", "ilike", self.request_partner_name)
            )

        return domain

    @staticmethod
    def _parse_sort_by(sort_by: str):
        # Order are of the form 'date_order.desc,partner_name.asc,id'
        sep = "."
        return {
            sort.split(sep)[0]: (
                "desc"
                if sep in sort and sort.split(sep)[1].lower() == "desc"
                else "asc"
            )
            for sort in (sort_by or "").split(",")
        }

    def to_odoo_order(self):
        if self.sort_by:
            sorts = self._parse_sort_by(self.sort_by)

            sort_fields = {
                "request_partner_name": "request_partner_name",
            }

            return ",".join(
                [
                    sort_fields[field] + (f" {order}" if order == "desc" else "")
                    for field, order in sorts.items()
                    if field in sort_fields
                ]
            )
        return "date_order desc"
