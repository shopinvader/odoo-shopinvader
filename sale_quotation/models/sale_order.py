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

    def action_request_quotation(self):
        if any(rec.state != "draft" or rec.typology != "cart" for rec in self):
            raise UserError(
                _(
                    "Only orders of cart typology in draft state "
                    "can be converted to quotation"
                )
            )
        self.write({"quotation_state": "customer_request", "typology": "sale"})
        return True

    def action_confirm_quotation(self):
        if any(rec.quotation_state != "waiting_acceptation" for rec in self):
            raise UserError(
                _(
                    "Only quotation with the state 'waiting_acceptation' can be "
                    "Confirmed."
                )
            )
        self.quotation_state = "accepted"
