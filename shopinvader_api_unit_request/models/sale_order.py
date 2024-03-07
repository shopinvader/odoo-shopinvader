# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    typology = fields.Selection(selection_add=[("request", "Request")])

    order_line_requested_ids = fields.One2many(
        "sale.order.line", "request_order_id", string="Accepted Lines"
    )
    order_line_rejected_ids = fields.One2many(
        "sale.order.line", "reject_order_id", string="Rejected Lines"
    )

    order_line_all_requested_ids = fields.One2many(
        "sale.order.line",
        compute="_compute_order_line_all_requested_ids",
        string="All Requested Lines",
    )

    @api.depends("order_line", "order_line_requested_ids")
    def _compute_order_line_all_requested_ids(self):
        for record in self:
            record.order_line_all_requested_ids = (
                record.order_line | record.order_line_requested_ids
            )

    def action_confirm_cart(self):
        for record in self:
            if record.typology == "request":
                raise UserError(_("You can't confirm a request."))
        return super().action_confirm_cart()

    def action_confirm(self):
        for record in self:
            if record.state == "request":
                raise UserError(_("You can't confirm a request."))

        res = super().action_confirm()

        # Notify partners of accepted and refused requests
        # Group accepted and refused by partners
        request_lines_by_partner = defaultdict(
            lambda: {
                "accepted": self.env["sale.order.line"],
                "rejected": self.env["sale.order.line"],
            }
        )

        for record in self:
            for line in record.order_line:
                if line.request_partner_id:
                    # Accepted line
                    request_lines_by_partner[line.request_partner_id][
                        "accepted"
                    ] |= line
            for line in record.order_line_rejected_ids:
                if line.request_partner_id:
                    # Rejected line
                    request_lines_by_partner[line.request_partner_id][
                        "rejected"
                    ] |= line

        for partner, lines in request_lines_by_partner.items():
            message = ""
            if lines["accepted"]:
                message += _("Your following requests have been accepted:\n")
                for line in lines["accepted"]:
                    message += f"{line.product_id.name} - {line.product_uom_qty}\n"

            if lines["rejected"]:
                message += _("Your following requests have been rejected:\n")
                for line in lines["rejected"]:
                    message += f"{line.product_id.name} - {line.product_uom_qty}"
                    if line.request_rejection_reason:
                        message += f": {line.request_rejection_reason}"
                    message += "\n"
            if not message:
                continue
            partner.message_post(
                body=message,
                subject=_("Request feedback for order %s") % record.name,
                subtype_id=self.env.ref("mail.mt_comment").id,
            )

        return res

    def action_request_cart(self):
        for record in self:
            if record.typology == "request":
                # cart is already requested
                continue
            record.order_line._action_request()
            record.write({"typology": "request"})
        return True
