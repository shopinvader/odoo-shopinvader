# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_customer_request_quotation(self):
        res = super().action_customer_request_quotation()
        for so in self:
            so.message_post(
                subject=_("Customer Quotation Request"),
                body=_(
                    'The quotation "%(quotation_name)s" has been requested '
                    'by the client "%(client)s".',
                    quotation_name=self.name,
                    client=self.partner_id.name,
                ),
                subtype_xmlid="sale_quotation_customer_quotation_workflow_notifications"
                ".mt_quotation_request",
            )
            self.env["mail.thread"].message_notify(
                partner_ids=self.partner_id.ids,
                subject=_("Quotation Request Confirmation"),
                body=_(
                    'Your quote request "%(quotation_name)s" has been successfully submitted.',
                    quotation_name=so.name,
                ),
                is_internal=False,
                email_add_signature=False,
                subtype_id=self.env.ref("mail.mt_comment").id,
            )

        return res

    def action_customer_accept_quotation(self):
        res = super().action_customer_accept_quotation()
        for so in self:
            so.message_post(
                subject=_("Customer Quotation Accepted"),
                body=_(
                    'The quotation "%(name)s" has been accepted by the client "%(client)s".',
                    name=self.name,
                    client=self.partner_id.name,
                ),
                subtype_xmlid="sale_quotation_customer_quotation_workflow_notifications"
                ".mt_customer_accept_quotation",
            )
        return res

    def action_customer_reset_quotation_to_draft(self):
        res = super().action_customer_reset_quotation_to_draft()
        for so in self:
            so.message_post(
                subject=_("Customer Quotation Reset to Draft"),
                body=_(
                    'The quotation "%(name)s" has been reset to draft by the '
                    'client "%(client)s".',
                    name=self.name,
                    client=self.partner_id.name,
                ),
                subtype_xmlid="sale_quotation_customer_quotation_workflow_notifications"
                ".mt_customer_reset_quotation_to_draft",
            )
        return res

    def action_customer_cancel_quotation(self):
        res = super().action_customer_cancel_quotation()
        for so in self:
            so.message_post(
                subject=_("Customer Quotation Cancelled"),
                body=_(
                    'The quotation "%(name)s" has been cancelled by the client "%(client)s".',
                    name=self.name,
                    client=self.partner_id.name,
                ),
                subtype_xmlid="sale_quotation_customer_quotation_workflow_notifications"
                ".mt_customer_cancel_quotation",
            )
        return res

    def _get_default_and_custom_subtype_ids(self):
        """Helper method to get the IDs of default messages subtypes depending.

        on the workflow of the given SO.
        """
        self.ensure_one()

        custom_quotation_subtype = self.env.ref(
            "sale_quotation_customer_quotation_workflow_notifications"
            ".mt_customer_quotation",
        )
        if self.use_customer_quotation_workflow:
            return (
                self.env["mail.message.subtype"]
                .search(
                    [
                        ("res_model", "=", "sale.order"),
                        ("parent_id", "=", custom_quotation_subtype.id),
                    ]
                )
                .filtered("default")
                .ids
            )
        return (
            self.env["mail.message.subtype"]
            .search(
                [
                    ("res_model", "in", [False, "sale.order"]),
                    ("parent_id", "!=", custom_quotation_subtype.id),
                ]
            )
            .filtered("default")
            .ids
        )

    def _update_subscriptions(self):
        """Helper method to handle subscription/unsubscription logic."""
        for so in self:
            follower_partner_ids = so.message_follower_ids.mapped("partner_id").ids

            if not follower_partner_ids:
                continue

            so.message_subscribe(
                partner_ids=follower_partner_ids,
                subtype_ids=so._get_default_and_custom_subtype_ids(),
            )

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res._update_subscriptions()
        return res

    def write(self, vals):
        res = super().write(vals)
        if "use_customer_quotation_workflow" in vals or "user_id" in vals:
            self._update_subscriptions()
        return res
