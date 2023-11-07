# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    shopinvader_state = fields.Selection(
        selection_add=[
            ("delivery_pending", "Not Delivered"),
            ("delivery_partial", "Partially Delivered"),
            ("delivery_full", "Fully Delivered"),
        ]
    )

    def _compute_shopinvader_state_depends(self):
        return super()._compute_shopinvader_state_depends() + ("delivery_status",)

    def _get_shopinvader_state(self):
        if not self.delivery_status:
            return super()._get_shopinvader_state()
        else:
            return "delivery_" + self.delivery_status
