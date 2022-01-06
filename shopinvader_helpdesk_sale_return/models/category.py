# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class HelpdeskTicketCategory(models.Model):
    _inherit = "helpdesk.ticket.category"

    automatically_generate_return_for = fields.Many2one(
        "delivery.carrier", domain=[("can_generate_return", "=", "True")]
    )
