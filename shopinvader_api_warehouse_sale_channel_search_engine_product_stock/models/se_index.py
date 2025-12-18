# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class SeIndex(models.Model):
    _inherit = "se.index"

    warehouse_ids = fields.Many2many(
        related="backend_id.sale_channel_id.warehouse_ids",
    )
