# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    shopinvader_state = fields.Selection(
        selection_add=[
            ("shipping_unprocessed", "No shipping yet"),
            ("shipping_partially", "Partially shipped"),
            ("shipping_done", "Fully shipped"),
        ]
    )

    def _compute_shopinvader_state_depends(self):
        return super()._compute_shopinvader_state_depends() + (
            "delivery_state",
        )

    def _get_shopinvader_state(self):
        if self.delivery_state == "no":
            return super()._get_shopinvader_state()
        return "shipping_" + self.delivery_state
