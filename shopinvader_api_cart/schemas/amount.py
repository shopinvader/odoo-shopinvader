# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo import _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round

from odoo.addons.pydantic import utils


class SaleAmount(BaseModel, metaclass=ExtendableModelMeta):
    tax: float
    untaxed: float
    total: float
    discount_total: float
    total_without_discount: float

    @classmethod
    def from_orm(cls, odoo_rec):
        """
        Build the class manually because the field aliases
        depend on the model name.
        """
        res = cls.construct()
        model = odoo_rec._name
        if model == "sale.order":
            sale = odoo_rec
        elif model == "sale.order.line":
            sale = odoo_rec.order_id
        else:
            raise UserError(
                _(f"Model {model} not supported in SaleAmount Pydantic model")
            )
        precision = sale.currency_id.decimal_places
        res.discount_total = float_round(odoo_rec.discount_total, precision)
        res.total_without_discount = float_round(
            odoo_rec.price_total_no_discount, precision
        )
        if model == "sale.order":
            res.tax = float_round(odoo_rec.amount_tax, precision)
            res.untaxed = float_round(odoo_rec.amount_untaxed, precision)
            res.total = float_round(odoo_rec.amount_total, precision)
        else:
            res.tax = float_round(odoo_rec.price_tax, precision)
            res.untaxed = float_round(odoo_rec.price_subtotal, precision)
            res.total = float_round(odoo_rec.price_total, precision)

        return res

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter


class SaleLineAmount(SaleAmount):
    price: float

    @classmethod
    def from_orm(cls, odoo_rec):
        res = super().from_orm(odoo_rec)
        res.price = odoo_rec.price_unit

        return res
