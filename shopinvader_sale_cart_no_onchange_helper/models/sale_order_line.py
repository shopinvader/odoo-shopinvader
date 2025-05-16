# Copyright 2025 CamptoCamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _play_onchanges_cart_line(self, vals):
        return vals
