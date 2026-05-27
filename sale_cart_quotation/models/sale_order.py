# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_request_quotation(self):
        if any(rec.state != "draft" or rec.typology != "cart" for rec in self):
            raise UserError(
                _(
                    "Only orders of cart typology in draft state "
                    "can be converted to quotation"
                )
            )
        self.write({"quotation_state": "customer_request", "typology": "sale"})
        self._send_request_notification()
        return True

    def _send_request_notification(self):
        template = self.env.ref("sale_cart_quotation.mail_template_request_quotation")
        for record in self:
            recipients = self.env["res.partner"]
            if record.user_id and record.user_id.partner_id:
                recipients |= record.user_id.partner_id

            if record.team_id:
                for member in record.team_id.member_ids:
                    recipients |= member.partner_id

            if not recipients:
                raise ValidationError(
                    _(
                        "Unable to send quotation request email because no "
                        "valid recipients (salesperson or sales team members) "
                        "were found for quotation %s." % record.name
                    )
                )

            # use the "mt_note" subtype to make sure only odoo users are notified
            # (not the client)
            record.with_context(
                mail_notify_author=True,  # author (ie user_id) is not notified by default
            ).message_post_with_template(
                template.id,
                email_layout_xmlid="mail.mail_notification_layout",
                subtype_id=self.env.ref("mail.mt_note").id,
                partner_ids=recipients.ids,
            )
