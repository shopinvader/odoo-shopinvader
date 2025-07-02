# Copyright 2017-2018 Akretion (http://www.akretion.com).
# Copyright 2021 Camptocamp (http://www.camptocamp.com)
# Copyright 2025 ACSONE SA/NV
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.exceptions import UserError


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

    typology = fields.Selection(
        selection_add=[("quote", "Quote")],
        default="quote",
        ondelete={
            "quote": "set default",
        },
    )

    use_customer_quotation_workflow = fields.Boolean(default=False)

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

    def action_confirm_quotation(self):
        self.quotation_state = "accepted"
        self.typology = "sale"

    def action_confirm(self):
        if (
            self.use_customer_quotation_workflow
            and self.env.context.get("use_quotation_confirm_wizard")
            and self.typology == "quote"
            and any(rec.quotation_state != "waiting_acceptation" for rec in self)
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
        else:
            self.action_confirm_quotation()
            return super(SaleOrder, self).action_confirm()

    def action_draft(self):
        self.typology = "quote"
        return super().action_draft()

    def action_toggle_customer_quotation_workflow(self):
        for order in self:
            if order.state != "draft":
                raise UserError(
                    _(
                        "Only sale orders in 'draft' state can toggle the quotation workflow."
                    )
                )
            order.use_customer_quotation_workflow = (
                not order.use_customer_quotation_workflow
            )
