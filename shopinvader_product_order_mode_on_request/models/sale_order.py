# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    shop_only_quotation = fields.Boolean(
        compute="_compute_shop_only_quotation", help=""
    )

    @api.depends("order_line.product_id.shop_order_mode")
    def _compute_shop_only_quotation(self):
        for record in self:
            record.shop_only_quotation = any(
                record.order_line.product_id.filtered(
                    lambda p: p.shop_order_mode == "quotation_only"
                )
            )
