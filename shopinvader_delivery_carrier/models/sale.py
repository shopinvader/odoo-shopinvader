# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    shopinvader_available_carrier_ids = fields.Many2many(
        compute="_compute_shopinvader_available_carrier_ids",
        comodel_name="delivery.carrier",
    )

    @api.multi
    @api.depends("shopinvader_backend_id")
    def _compute_shopinvader_available_carrier_ids(self):
        for order in self.filtered("shopinvader_backend_id"):
            carriers = order.shopinvader_backend_id.carrier_ids
            carriers = order.available_carrier_ids & carriers
            order.shopinvader_available_carrier_ids = carriers

    def _get_available_carrier(self):
        self.ensure_one()
        return self.shopinvader_available_carrier_ids.sorted(
            lambda c: c.rate_shipment(self).get("price", 0.0)
        )
