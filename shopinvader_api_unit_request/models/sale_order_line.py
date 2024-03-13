# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_requested = fields.Float(
        string="Quantity Requested",
        help="Quantity requested by the collaborator in case of a request.",
        default=0.0,
    )

    request_partner_id = fields.Many2one(
        "res.partner",
        string="Request Partner",
        help="The partner who requested this line.",
    )
    request_order_id = fields.Many2one(
        "sale.order",
        string="Request Order",
        help="The order that requested this line.",
    )
    reject_order_id = fields.Many2one(
        "sale.order",
        string="Reject Order",
        help="The order that rejected this line.",
    )
    request_rejected = fields.Boolean(
        help="The request has been rejected.",
        default=False,
    )
    request_rejection_reason = fields.Text(
        help="The reason of the rejection.",
    )
    request_accepted = fields.Boolean(
        help="The request has been accepted.",
        compute="_compute_request_accepted",
    )

    @api.depends("request_order_id")
    def _compute_request_accepted(self):
        for record in self:
            record.request_accepted = record.request_order_id

    def _action_request(self):
        for record in self:
            record.qty_requested = record.product_uom_qty
            record.request_partner_id = record.order_id.partner_id

    def _action_accept_request(self, target_order):
        for record in self:
            record.request_order_id = record.order_id
            record.order_id = target_order
        return True

    def _action_reject_request(self, target_order, reason):
        for record in self:
            record.request_rejected = True
            record.reject_order_id = target_order
            record.request_rejection_reason = reason
        return True

    def _action_reset_request(self):
        for record in self:
            record.request_rejected = False
            record.reject_order_id = False
            record.request_rejection_reason = False
        return True

    def unlink(self):
        for record in self:
            if record.request_partner_id and record.request_order_id:
                record.order_id = record.request_order_id
                record.request_order_id = False
                record.product_uom_qty = record.qty_requested
                self -= record

        return super().unlink()
