# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    shopinvader_state = fields.Selection(
        [
            ("cancel", "Cancel"),
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("shipped", "Shipped"),
        ],
        compute="_compute_shopinvader_state",
        store=True,
    )

    def _get_shopinvader_state(self):
        self.ensure_one()
        if self.state == "cancel":
            return "cancel"
        elif self.state == "done":
            return "shipped"
        elif self.state == "draft":
            return "pending"
        else:
            return "processing"

    def _compute_shopinvader_state_depends(self):
        return ("state",)

    @api.depends(lambda self: self._compute_shopinvader_state_depends())
    def _compute_shopinvader_state(self):
        # simple way to have more human friendly name for
        # the sale order on the website
        for record in self:
            record.shopinvader_state = record._get_shopinvader_state()
