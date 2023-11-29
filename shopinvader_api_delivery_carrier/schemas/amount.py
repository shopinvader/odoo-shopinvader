# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools import float_round

from odoo.addons.shopinvader_schema_sale.schemas import amount


class SaleAmount(amount.SaleAmount, extends=True):
    tax_without_shipping: float = 0
    untaxed_without_shipping: float = 0
    total_without_shipping: float = 0
    total_without_shipping_without_discount: float = 0

    @classmethod
    def from_sale_order(cls, sale_order):
        res = super().from_sale_order(sale_order)
        res.tax_without_shipping = sale_order.item_amount_tax
        res.untaxed_without_shipping = sale_order.item_amount_untaxed
        res.total_without_shipping = sale_order.item_amount_total
        res.total_without_shipping_without_discount = float_round(
            sale_order.item_amount_total - sale_order.discount_total,
            sale_order.currency_id.decimal_places,
        )

        return res
