# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    shopinvader_delivery_state = fields.Selection(
        [
            ("shipping_no", "No shipping"),
            ("shipping_unprocessed", "No shipping yet"),
            ("shipping_partially", "Partially shipped"),
            ("shipping_done", "Fully shipped"),
        ],
        compute="_compute_shopinvader_delivery_state",
        store=True,
    )

    def _get_shopinvader_delivery_state(self):
        return "shipping_" + self.delivery_state

    def _compute_shopinvader_delivery_state_depends(self):
        return ("delivery_state",)

    @api.depends(
        lambda self: self._compute_shopinvader_delivery_state_depends()
    )
    def _compute_shopinvader_delivery_state(self):
        for record in self:
            record.shopinvader_delivery_state = (
                record._get_shopinvader_delivery_state()
            )
