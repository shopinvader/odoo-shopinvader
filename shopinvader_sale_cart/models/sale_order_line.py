# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    @api.model
    def _play_onchanges_cart_line(self, vals):
        return self.sudo().play_onchanges(vals, vals.keys())
