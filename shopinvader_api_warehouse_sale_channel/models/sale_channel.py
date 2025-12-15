# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleChannel(models.Model):
    _inherit = "sale.channel"

    warehouse_ids = fields.Many2many(
        "stock.warehouse",
        string="Warehouses",
        help="Warehouses associated with this sale channel.",
    )
