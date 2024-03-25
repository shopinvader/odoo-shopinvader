# Copyright 2024 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, exceptions, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    cart_step_id = fields.Many2one(
        comodel_name="sale.order.cart.step", string="Current cart step", readonly=True
    )
    cart_step_done_ids = fields.Many2many(
        comodel_name="sale.order.cart.step",
        string="Done cart steps",
        readonly=True,
    )

    def cart_step_update(self, current_step=None, next_step=None):
        vals = self._cart_step_update_vals(
            current_step=current_step, next_step=next_step
        )
        if vals:
            self.write(vals)

    def _cart_step_update_vals(self, current_step=None, next_step=None):
        vals = {}
        if current_step:
            vals["cart_step_done_ids"] = [
                (4, self._cart_step_get_from_code(current_step).id, 0)
            ]
        if next_step:
            vals["cart_step_id"] = self._cart_step_get_from_code(next_step).id
        return vals

    def _cart_step_get_from_code(self, code):
        step = self.env["sale.order.cart.step"].search([("code", "=", code)], limit=1)
        if not step:
            raise exceptions.UserError(_("Invalid step code %s") % code)
        return step
