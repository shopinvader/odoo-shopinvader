# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Auto set the sale_channel_id from the fastapi context
    sale_channel_id = fields.Many2one(
        default=lambda self: self.env.context.get("sale_channel_id"),
    )
