# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.extendable_fastapi import StrictExtendableBaseModel
from odoo.addons.shopinvader_api_cart.schemas import cart
from odoo.addons.shopinvader_schema_sale.schemas import sale_line


class SaleLineOptions(StrictExtendableBaseModel):
    @classmethod
    def from_sale_order_line(cls, odoo_rec):
        return cls.model_construct()


class SaleLine(sale_line.SaleLine, extends=True):
    options: SaleLineOptions

    @classmethod
    def from_sale_order_line(cls, odoo_rec):
        res = super().from_sale_order_line(odoo_rec)
        res.options = SaleLineOptions.from_sale_order_line(odoo_rec)
        return res


class CartTransaction(cart.CartTransaction, extends=True):
    options: SaleLineOptions | None = None
