# Copyright 2024 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    visible_in_shopinvader_api = fields.Boolean(
        compute="_compute_visible_in_shopinvader_api", store=True
    )

    def _is_visible_in_shopinvader_api(self):
        self.ensure_one()
        return True

    @api.depends("product_id")
    def _compute_visible_in_shopinvader_api(self):
        for record in self:
            record.visible_in_shopinvader_api = record._is_visible_in_shopinvader_api()
