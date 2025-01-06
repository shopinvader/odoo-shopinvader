# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models

from odoo.addons.sale.models.sale_order import SaleOrder
from odoo.addons.shopinvader_api_cart.schemas import CartTransaction


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    carving = fields.Char()
    special = fields.Boolean()

    def _match_cart_line(
        self,
        product_id,
        carving=None,
        special=None,
        **kwargs,
    ):
        rv = super()._match_cart_line(
            product_id,
            carving=carving,
            special=special,
            **kwargs,
        )
        return rv and self.carving == carving and self.special == special

    def _prepare_cart_line_transfer_values(self):
        vals = super()._prepare_cart_line_transfer_values()
        vals["carving"] = self.carving
        vals["special"] = self.special
        return vals


class ShopinvaderApiCartRouterHelper(
    models.AbstractModel
):  # pylint: disable=consider-merging-classes-inherited
    _inherit = "shopinvader_api_cart.cart_router.helper"

    @api.model
    def _apply_transactions_creating_new_cart_line_prepare_vals(
        self, cart: SaleOrder, transactions: list[CartTransaction], values: dict
    ):
        options = transactions[0].options
        if options:
            values["carving"] = options.engraving
            values["special"] = options.special

        return values
