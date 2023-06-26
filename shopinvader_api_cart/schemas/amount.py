# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.tools.float_utils import float_round

from odoo.addons.pydantic import utils


class SaleAmount(BaseModel, metaclass=ExtendableModelMeta):
    tax: float
    untaxed: float
    total: float
    discount_total: float
    total_without_discount: float

    @classmethod
    def from_sale_order(cls, sale_order):
        res = cls.construct()
        precision = sale_order.currency_id.decimal_places
        res.discount_total = float_round(sale_order.discount_total, precision)
        res.total_without_discount = float_round(
            sale_order.price_total_no_discount, precision
        )
        res.tax = float_round(sale_order.amount_tax, precision)
        res.untaxed = float_round(sale_order.amount_untaxed, precision)
        res.total = float_round(sale_order.amount_total, precision)

        return res

    @classmethod
    def from_sale_order_line(cls, order_line):
        res = cls.construct()
        precision = order_line.order_id.currency_id.decimal_places
        res.discount_total = float_round(order_line.discount_total, precision)
        res.total_without_discount = float_round(
            order_line.price_total_no_discount, precision
        )
        res.tax = float_round(order_line.price_tax, precision)
        res.untaxed = float_round(order_line.price_subtotal, precision)
        res.total = float_round(order_line.price_total, precision)

        return res

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter


class SaleLineAmount(SaleAmount):
    price: float

    @classmethod
    def from_sale_order_line(cls, order_line):
        res = super().from_sale_order_line(order_line)
        res.price = order_line.price_unit
        return res
