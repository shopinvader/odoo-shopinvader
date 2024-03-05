# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from extendable_pydantic import StrictExtendableBaseModel
from pydantic import Field

from odoo import api

from odoo.addons.shopinvader_schema_sale.schemas.sale_line import SaleLine


class SaleLineWithSale(SaleLine):
    order_id: int

    @classmethod
    def from_sale_order_line(cls, odoo_rec):
        res = super().from_sale_order_line(odoo_rec)
        res.order_id = odoo_rec.order_id.id
        return res


class SaleLineSearch(StrictExtendableBaseModel, extra="ignore"):
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
        if self.order_name:
            domain.append(("order_id.name", "ilike", self.order_name))

        if self.product_name:
            domain.append(("product_id.name", "ilike", self.product_name))

        return domain
