from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    reward_amount_tax_incl = fields.Float(compute="_compute_reward_total_tax_incl")
    promo_codes = fields.Char(compute="_compute_promo_codes")
    generated_coupon_ids = fields.One2many(
        "loyalty.card",
        "order_id",
        "Generated Coupons",
        help="The coupons generated from this order.",
    )
    code_program_ids = fields.Many2many(
        "loyalty.program", string="Programs with code", compute="_compute_programs"
    )
    no_code_program_ids = fields.Many2many(
        "loyalty.program", string="Programs without code", compute="_compute_programs"
    )

    def _get_reward_lines(self):
        self.ensure_one()
        return self.order_line.filtered("is_reward_line")

    @api.depends("order_line")
    def _compute_reward_total_tax_incl(self):
        for order in self:
            reward_amount_tax_incl = 0
            for line in order._get_reward_lines():
                if line.reward_id.reward_type != "product":
                    reward_amount_tax_incl += line.price_subtotal
                else:
                    # Free product are 'regular' product lines with a price_unit of 0
                    reward_amount_tax_incl -= (
                        line.product_id.lst_price * line.product_uom_qty
                    )
            order.reward_amount_tax_incl = reward_amount_tax_incl

    @api.depends("order_line", "applied_coupon_ids", "code_enabled_rule_ids")
    def _compute_promo_codes(self):
        for order in self:
            codes = order.applied_coupon_ids.mapped(
                "code"
            ) + order.code_enabled_rule_ids.mapped("code")
            if codes:
                order.promo_codes = str(codes)  # stock the list of codes in a string
            else:
                order.promo_codes = ""

    @api.depends("order_line", "applied_coupon_ids", "code_enabled_rule_ids")
    def _compute_programs(self):
        self.no_code_program_ids = self.env["loyalty.program"]
        self.code_program_ids = self.env["loyalty.program"]
        for order in self:
            # Consider claimable rewards
            order._update_programs_and_rewards()
            res = order._get_claimable_rewards()
            for coupon, _ in res.items():
                if coupon.program_id.trigger == "auto":
                    order.no_code_program_ids |= coupon.program_id
                else:
                    order.code_program_ids |= coupon.program_id

            # Consider applied rewards
            programs = order._get_reward_lines().mapped("reward_id.program_id")
            order.no_code_program_ids |= programs.filtered(
                lambda p: p.trigger == "auto"
            )
            order.code_program_ids |= programs.filtered(
                lambda p: p.trigger == "with_code"
            )
