# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    api_type = fields.Char(compute="_compute_api_type")

    def _get_api_type(self):
        self.ensure_one()
        if self.display_type == "line_section":
            return "section"
        if self.display_type == "line_note":
            return "note"
        return "product"

    @api.depends("display_type")
    def _compute_api_type(self):
        for sol in self:
            sol.api_type = sol._get_api_type()
