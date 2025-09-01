# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime
from typing import Annotated

from extendable_pydantic import StrictExtendableBaseModel
from pydantic import Field

from odoo import api

from odoo.addons.shopinvader_schema_sale.schemas.sale_line import SaleLine


class SaleOrderFromLine(StrictExtendableBaseModel):
    id: int
    name: str
    state: str
    date_order: datetime

    @classmethod
    def from_sale_order(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            name=odoo_rec.name,
            state=odoo_rec.state,
            date_order=odoo_rec.date_order,
        )


class SaleLineWithSale(SaleLine):
    order: SaleOrderFromLine

    @classmethod
    def from_sale_order_line(cls, odoo_rec):
        res = super().from_sale_order_line(odoo_rec)
        res.order = SaleOrderFromLine.from_sale_order(odoo_rec.order_id)
        return res


class SaleLineSearch(StrictExtendableBaseModel, extra="ignore"):
    order_id: Annotated[
        int | None,
        Field(
            description="When used, the search look for any sale order lines "
            "where the order id is equal to the given value."
        ),
    ] = None
    order_name: Annotated[
        str | None,
        Field(
            description="When used, the search look for any sale order lines "
            "where the order name contains the given value case insensitively."
        ),
    ] = None
    product_name: Annotated[
        str | None,
        Field(
            description="When used, the search look for any sale order lines "
            "where the product name contains the given value case insensitively."
        ),
    ] = None

    def to_odoo_domain(self, env: api.Environment):
        domain = []

        if self.order_id:
            domain.append(("order_id", "=", self.order_id))

        if self.order_name:
            domain.append(("order_id.name", "ilike", self.order_name))

        if self.product_name:
            domain.append(("product_id.name", "ilike", self.product_name))

        return domain
