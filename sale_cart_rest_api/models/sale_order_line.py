# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import float_compare


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    def _transactions_to_record_write(self, transactions):
        """Apply transactions to current line and return a record write command
        to apply to the one2many field on SO."""
        self.ensure_one()
        delta_qty = sum(t["qty"] for t in transactions)
        new_qty = self.product_uom_qty + delta_qty
        if (
            float_compare(
                new_qty, 0, precision_rounding=self.product_uom.rounding
            )
            <= 0
        ):
            return (2, self.id, None)
        vals = {"product_uom_qty": new_qty}
        vals.update(self.play_onchanges(vals, vals.keys()))
        return (1, self.id, vals)

    @api.model
    def _transactions_to_record_create(self, sale_order, transactions):
        """Create a record create command to apply to the one2many field on SO
        from transactions."""
        vals = self._prepare_line_from_transactions(
            sale_order=sale_order, transactions=transactions
        )
        if vals:
            vals.update(self.play_onchanges(vals, vals.keys()))
        return (0, None, vals)

    @api.model
    def _prepare_line_from_transactions(self, sale_order, transactions):
        delta_qty = sum(t["qty"] for t in transactions)
        if (
            float_compare(
                delta_qty, 0, precision_rounding=self.product_uom.rounding
            )
            <= 0
        ):
            return None
        partner = sale_order.partner_id
        vals = {
            "product_id": transactions[0]["product_id"],
            "product_uom_qty": delta_qty,
            "order_id": sale_order.id,
        }
        ctx_lang = self.env.context.get("lang", partner.lang)
        if partner.lang != ctx_lang:
            product_id = vals["product_id"]
            vals["name"] = self._get_sale_order_line_name(product_id)
        return vals

    def _get_sale_order_line_name(self, product_id):
        product = self.env["product.product"].browse(product_id)
        name = product.name_get()[0][1]
        if product.description_sale:
            name += "\n" + product.description_sale
        return name
