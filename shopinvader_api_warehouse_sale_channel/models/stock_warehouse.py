# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    sale_channel_ids = fields.Many2many(
        "sale.channel",
        string="Sale Channels",
        help="Sale channels associated with this warehouse.",
    )
