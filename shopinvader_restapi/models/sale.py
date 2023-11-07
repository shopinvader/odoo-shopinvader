# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "track.external.mixin"]

    shopinvader_backend_id = fields.Many2one("shopinvader.backend", "Backend")
    current_step_id = fields.Many2one(
        "shopinvader.cart.step", "Current Cart Step", readonly=True
    )
    done_step_ids = fields.Many2many(
        comodel_name="shopinvader.cart.step",
        string="Done Cart Step",
        readonly=True,
    )

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res["shopinvader_backend_id"] = self.shopinvader_backend_id.id
        return res

    def _confirm_cart(self):
        self.ensure_one()
        res = super()._confirm_cart()
        if self.shopinvader_backend_id:
            self.shopinvader_backend_id._send_notification("cart_confirmation", self)
        return res

    def _confirm_sale(self):
        self.ensure_one()
        res = super()._confirm_sale()
        if self.shopinvader_backend_id:
            self.shopinvader_backend_id._send_notification("sale_confirmation", self)
        return res

    def reset_price_tax(self):
        for record in self:
            record.order_line.reset_price_tax()

    def _need_price_update(self, vals):
        for field in ["fiscal_position_id", "pricelist_id"]:
            if field in vals and self[field].id != vals[field]:
                return True
        return False

    def write_with_onchange(self, vals):
        self.ensure_one()
        # Playing onchange on one2many is not really really clean
        # all value are returned even if their are not modify
        # Moreover "convert_to_onchange" in field.py add (5,) that
        # will drop the order_line
        # so it's better to drop the key order_line and run the onchange
        # on line manually
        reset_price = False
        new_vals = self.play_onchanges(vals, vals.keys())
        new_vals.pop("order_line", None)
        vals.update(new_vals)
        reset_price = self._need_price_update(vals)
        self.write(vals)
        if reset_price:
            self.reset_price_tax()
        return True

    def _send_order_confirmation_mail(self):
        non_shopinvader_orders = self.env["sale.order"].browse()
        for order in self:
            # Only send emails through shopinvader notifications
            # When order are done from website
            if not order.shopinvader_backend_id:
                non_shopinvader_orders |= order
        return super(SaleOrder, non_shopinvader_orders)._send_order_confirmation_mail()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def reset_price_tax(self):
        for line in self:
            line._compute_tax_id()
            line._compute_discount()
