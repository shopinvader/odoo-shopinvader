# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    note = fields.Char()


class ShopinvaderApiCartRouterHelper(models.AbstractModel):
    _inherit = "shopinvader_api_cart.cart_router.helper"

    @api.model
    def _prepare_line_from_transactions(self, cart, transactions):
        vals = super()._prepare_line_from_transactions(cart, transactions)
        # if the qty delta (add and remove of a product) is 0 then the vals is None
        if vals:
            options = transactions[0].options
            if options and options.note:
                vals["note"] = options.note
        return vals
