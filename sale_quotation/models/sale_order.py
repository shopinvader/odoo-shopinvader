# Copyright 2017-2018 Akretion (http://www.akretion.com).
# Copyright 2021 Camptocamp (http://www.camptocamp.com)
# Copyright 2025 ACSONE SA/NV
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.sale.models.sale_order import READONLY_FIELD_STATES

from ..exceptions import InvalidQuotationStateError


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
        tracking=True,
    )

    typology = fields.Selection(
        selection_add=[("quote", "Quote")],
        ondelete={
            "quote": "set default",
        },
    )

    use_customer_quotation_workflow = fields.Boolean(
        inverse="_inverse_use_customer_quotation_workflow",
        default=False,
        states=READONLY_FIELD_STATES,
    )

    is_action_customer_request_quotation_allowed = fields.Boolean(
        compute="_compute_is_action_customer_request_quotation_allowed"
    )

    is_action_customer_accept_quotation_allowed = fields.Boolean(
        compute="_compute_is_action_customer_accept_quotation_allowed"
    )
    is_action_customer_reset_quotation_to_draft_allowed = fields.Boolean(
        compute="_compute_is_action_customer_reset_quotation_to_draft_allowed"
    )
    is_action_customer_cancel_quotation_allowed = fields.Boolean(
        compute="_compute_is_action_customer_cancel_quotation_allowed"
    )

    def _inverse_use_customer_quotation_workflow(self):
        """Set the typology to 'quote' when enabling the customer quotation workflow."""
        for order in self:
            if order.use_customer_quotation_workflow and order.typology != "quote":
                order.typology = "quote"
            elif (
                not order.use_customer_quotation_workflow and order.typology == "quote"
            ):
                order.typology = "sale"

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

    @api.depends("use_customer_quotation_workflow", "quotation_state")
    def _compute_is_action_customer_request_quotation_allowed(self):
        for order in self:
            order.is_action_customer_request_quotation_allowed = (
                order._check_customer_action_allowed(
                    "request_quotation", raise_exception=False
                )
            )

    @api.depends("use_customer_quotation_workflow", "quotation_state")
    def _compute_is_action_customer_accept_quotation_allowed(self):
        for order in self:
            order.is_action_customer_accept_quotation_allowed = (
                order._check_customer_action_allowed(
                    "accept_quotation", raise_exception=False
                )
            )

    @api.depends("use_customer_quotation_workflow", "quotation_state")
    def _compute_is_action_customer_reset_quotation_to_draft_allowed(self):
        for order in self:
            order.is_action_customer_reset_quotation_to_draft_allowed = (
                order._check_customer_action_allowed(
                    "reset_to_draft", raise_exception=False
                )
            )

    @api.depends("use_customer_quotation_workflow", "quotation_state")
    def _compute_is_action_customer_cancel_quotation_allowed(self):
        for order in self:
            order.is_action_customer_cancel_quotation_allowed = (
                order._check_customer_action_allowed(
                    "cancel_quotation", raise_exception=False
                )
            )

    @property
    def _customer_actions_by_quotation_state(self):
        """Customer actions available for each state of the quotation workflow."""
        return {
            "draft": ["request_quotation"],
            "customer_request": [
                "reset_to_draft",
                "cancel_quotation",
                "quotation_sent",
            ],
            "waiting_acceptation": [
                "reset_to_draft",
                "cancel_quotation",
                "accept_quotation",
            ],
            "cancel": ["reset_to_draft"],
            "accepted": [],
        }

    def _check_customer_action_allowed(self, action, raise_exception=True):
        """Check if the action is allowed for the current quotation state."""
        for rec in self:
            exception = None
            if not rec.use_customer_quotation_workflow:
                exception = UserError(
                    _("Customer quotation workflow is not enabled for this order.")
                )
            elif action not in self._customer_actions_by_quotation_state.get(
                rec.quotation_state, []
            ):
                expected_states = []
                for (
                    quotation_sate,
                    actions,
                ) in self._customer_actions_by_quotation_state.items():
                    if action in actions:
                        expected_states.append(quotation_sate)
                exception = InvalidQuotationStateError(
                    self.env,
                    action=action,
                    expected_states=expected_states,
                    current_state=self.quotation_state,
                )
            if exception:
                if raise_exception:
                    raise exception
                return False
        return True

    def action_customer_request_quotation(self):
        self._check_customer_action_allowed("request_quotation")
        self.quotation_state = "customer_request"
        return True

    def action_customer_accept_quotation(self):
        self._check_customer_action_allowed("accept_quotation")
        return self.action_confirm()

    def action_customer_reset_quotation_to_draft(self):
        self._check_customer_action_allowed("reset_to_draft")
        return self.action_draft()

    def action_customer_cancel_quotation(self):
        self._check_customer_action_allowed("cancel_quotation")
        self.quotation_state = "cancel"
        return self.with_context(disable_cancel_warning=True).action_cancel()

    def action_confirm(self):
        customer_quotations = self.filtered("use_customer_quotation_workflow")
        if (
            customer_quotations
            and self.env.context.get("use_quotation_confirm_wizard")
            and any(
                rec.quotation_state not in ("waiting_acceptation", "accepted")
                for rec in customer_quotations
            )
        ):
            return {
                "name": _("Confirm Sale Order"),
                "type": "ir.actions.act_window",
                "res_model": "sale.order.confirm.warning.wizard",
                "views": [[False, "form"]],
                "target": "new",
                "context": {
                    "default_sale_order_ids": self.ids,
                    "default_message": _(
                        "The selected quotation(s) are not in 'Waiting Acceptation' "
                        "state. Are you sure you want to confirm them?"
                    ),
                },
            }
        customer_quotations.quotation_state = "accepted"
        customer_quotations.typology = "sale"
        return super().action_confirm()

    def action_draft(self):
        customer_quotations = self.filtered("use_customer_quotation_workflow")
        customer_quotations.quotation_state = "draft"
        customer_quotations.filtered(
            lambda so: so.typology != "quote"
        ).typology = "quote"
        return super().action_draft()

    def action_quotation_sent(self):
        customer_quotations = self.filtered("use_customer_quotation_workflow")
        if customer_quotations:
            customer_quotations._check_customer_action_allowed("quotation_sent")
        return super().action_quotation_sent()
