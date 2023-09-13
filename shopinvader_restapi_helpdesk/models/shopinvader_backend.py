# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    helpdesk_channel_id = fields.Many2one(
        comodel_name="helpdesk.ticket.channel",
        help="The channel used in the helpdesk tickets",
        default=lambda self: self.env.ref("helpdesk_mgmt.helpdesk_ticket_channel_web"),
    )
