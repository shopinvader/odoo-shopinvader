# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import float_compare

from ..schemas import CartTransaction


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    @api.model
    def _play_onchanges_cart(self, vals):
        return self.sudo().play_onchanges(vals, vals.keys())

    def _transactions_to_record_write(self, transactions: list[CartTransaction]):
        """Apply transactions to current line and return a record write command
        to apply to the one2many field on SO.

        :param transactions: a list of CartTransaction Pydantic records
        """
        self.ensure_one()
        delta_qty = sum(t.qty for t in transactions)
        new_qty = self.product_uom_qty + delta_qty
        if float_compare(new_qty, 0, precision_rounding=self.product_uom.rounding) <= 0:
            return (2, self.id, None)
        vals = {"product_uom_qty": new_qty}
        vals.update(self._play_onchanges_cart(vals))
        return (1, self.id, vals)

    @api.model
    def _transactions_to_record_create(self, sale_order, transactions):
        """Create a record create command to apply to the one2many field on SO
        from transactions.

        :param transactions: a list of CartTransaction Pydantic records
        """
        vals = self._prepare_line_from_transactions(
            sale_order=sale_order, transactions=transactions
        )
        if vals:
            vals.update(self._play_onchanges_cart(vals))
            return (0, None, vals)
        return None

    @api.model
    def _prepare_line_from_transactions(self, sale_order, transactions):
        """
        :param transactions: a list of CartTransaction Pydantic records
        """
        delta_qty = sum(t.qty for t in transactions)
        product_id = (transactions[0]).product_id
        product_uom = self.env["product.product"].browse(product_id).uom_id
        if float_compare(delta_qty, 0, precision_rounding=product_uom.rounding) <= 0:
            return None
        partner = sale_order.partner_id
        vals = {
            # Order in this dict is important and must be kept.
            # When creating the transaction we call play_onchanges().
            # These onchanges will be played following the order defined here.
            # All computes depending on order_id must be triggered first,
            # to set the currency on the SOL for e.g.
            "order_id": sale_order.id,
            "product_id": product_id,
            "product_uom_qty": delta_qty,
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
