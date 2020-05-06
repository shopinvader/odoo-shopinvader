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

    @api.depends("shopinvader_backend_id")
    def _compute_shopinvader_available_carrier_ids(self):
        carrier = self.env["delivery.carrier"]
        for order in self:
            if not order.shopinvader_backend_id:
                order.shopinvader_available_carrier_ids = carrier
                continue
            order.shopinvader_available_carrier_ids = (
                order._available_carriers()
                & order.shopinvader_backend_id.carrier_ids
            )

    def _available_carriers(self):
        carriers = self.env["delivery.carrier"].search(
            [
                "|",
                ("company_id", "=", False),
                ("company_id", "=", self.company_id.id),
            ]
        )
        return (
            carriers.available_carriers(self.partner_shipping_id)
            if self.partner_id
            else carriers
        )

    def _invader_available_carriers(self):
        self.ensure_one()
        return self.shopinvader_available_carrier_ids.sorted(
            lambda c: c.rate_shipment(self).get("price", 0.0)
        )

    def _set_carrier_and_price(self, carrier_id):
        wizard = (
            self.env["choose.delivery.carrier"]
            .with_context(
                {"default_order_id": self.id, "default_carrier_id": carrier_id}
            )
            .create({})
        )
        wizard._onchange_carrier_id()
        wizard.button_confirm()
        return wizard.delivery_price
