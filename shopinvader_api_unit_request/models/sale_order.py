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
            if not lines["accepted"] and not lines["rejected"]:
                continue
            self._notify_partner_on_request_feedback(
                partner, lines["accepted"], lines["rejected"]
            )

        return res

    def _notify_partner_on_request_feedback(
        self, partner, accepted_lines, rejected_lines
    ):
        """Override this method to customize the notification message.
        Sending a mail template for example.

        :param partner: res.partner record Concerned partner
        :param accepted_lines: sale.order.line recordset Accepted lines
        :param rejected_lines: sale.order.line recordset Rejected lines
        """
        message = ""
        if accepted_lines:
            message += _("Your following requests have been accepted:\n")
            for line in accepted_lines:
                message += f"{line.product_id.name} - {line.product_uom_qty}\n"

        if rejected_lines:
            message += _("Your following requests have been rejected:\n")
            for line in rejected_lines:
                message += f"{line.product_id.name} - {line.product_uom_qty}"
                if line.request_rejection_reason:
                    message += f": {line.request_rejection_reason}"
                message += "\n"

        partner.message_post(
            body=message,
            subject=_("Request feedback"),
            subtype_id=self.env.ref("mail.mt_comment").id,
        )

    def action_request_cart(self):
        for record in self:
            if record.typology == "request":
                # cart is already requested
                continue
            record.order_line._action_request()
            record.write({"typology": "request"})
        return True
