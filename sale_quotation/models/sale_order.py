# Copyright 2017-2018 Akretion (http://www.akretion.com).
# Copyright 2021 Camptocamp (http://www.camptocamp.com)
# Copyright 2025 ACSONE SA/NV
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    quotation_state = fields.Selection(
        selection=[
            ("cancel", "Cancel"),
            ("draft", "Draft"),
            ("customer_request", "Customer Request"),
            ("waiting_acceptation", "Waiting Acceptation"),
            ("accepted", "Accepted"),
        ],
        compute="_compute_quotation_state",
        store=True,
        readonly=False,
        copy=False,
    )

    typology = fields.Selection(selection_add=[("quote", "Quote")], default="quote")

    @api.depends("state")
    def _compute_quotation_state(self):
        for record in self:
            if record.state == "cancel":
                record.quotation_state = "cancel"
            elif record.state == "draft" and record.quotation_state not in (
                "customer_request",
                "waiting_acceptation",
                "accepted",
            ):
                record.quotation_state = "draft"
            elif record.state == "sent" and record.quotation_state != "accepted":
                record.quotation_state = "waiting_acceptation"
            elif record.state == "sale":
                record.quotation_state = "accepted"

    def _send_confirmation_email_to_sales_person_and_sales_team(self):
        template = self.env.ref(
            "sale_quotation.mail_template_quotation_accepted_for_sales_team"
        )
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
                        "Unable to send confirmation email because no valid "
                        "recipients (salesperson or sales team members) "
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

    def action_confirm_quotation(self):
        if any(rec.quotation_state != "waiting_acceptation" for rec in self):
            raise UserError(
                _(
                    "Only quotation with the state 'waiting_acceptation' can be "
                    "Confirmed."
                )
            )
        for record in self:
            record.quotation_state = "accepted"
            record.typology = "sale"
            record._send_confirmation_email_to_sales_person_and_sales_team()

    def action_confirm(self):
        for record in self:
            if record.typology == "quote":
                record.action_confirm_quotation()
        return super().action_confirm()

    def action_draft(self):
        self.typology = "quote"
        return super().action_draft()
