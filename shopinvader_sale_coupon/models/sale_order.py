from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    reward_amount_tax_incl = fields.Float(compute="_compute_reward_total_tax_incl")

    @api.depends("order_line")
    def _compute_reward_total_tax_incl(self):
        for order in self:
            order.reward_amount_tax_incl = sum(
                [
                    line.price_subtotal + line.price_tax
                    for line in order._get_reward_lines()
                ]
            )
