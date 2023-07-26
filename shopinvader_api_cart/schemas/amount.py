# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel, Field

from odoo.tools.float_utils import float_round


class SaleAmount(BaseModel, metaclass=ExtendableModelMeta):
    tax: float = Field(description="Tax amount")
    untaxed: float = Field(description="Amount untaxed")
    total: float = Field(description="Total amount")
    discount_total: float
    total_without_discount: float

    @classmethod
    def from_sale_order(cls, sale_order):
        precision = sale_order.currency_id.decimal_places
        return cls.model_construct(
            discount_total=float_round(sale_order.discount_total, precision),
            total_without_discount=float_round(
                sale_order.price_total_no_discount, precision
            ),
            tax=float_round(sale_order.amount_tax, precision),
            untaxed=float_round(sale_order.amount_untaxed, precision),
            total=float_round(sale_order.amount_total, precision),
        )

    @classmethod
    def from_sale_order_line(cls, order_line):
        precision = order_line.order_id.currency_id.decimal_places
        return cls.model_construct(
            discount_total=float_round(order_line.discount_total, precision),
            total_without_discount=float_round(
                order_line.price_total_no_discount, precision
            ),
            tax=float_round(order_line.price_tax, precision),
            untaxed=float_round(order_line.price_subtotal, precision),
            total=float_round(order_line.price_total, precision),
        )


class SaleLineAmount(SaleAmount):
    price: float = Field(description="Unit price")

    @classmethod
    def from_sale_order_line(cls, order_line):
        res = super().from_sale_order_line(order_line)
        res.price = order_line.price_unit
        return res
