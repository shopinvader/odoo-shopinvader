# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import Component


class TicketService(Component):
    """Shopinvader service to manage helpdesk tickets."""

    _name = "helpdesk.ticket.service"
    _inherit = ["helpdesk.ticket.service", "base.shopinvader.service"]
    _collection = "shopinvader.backend"

    def _prepare_params(self, params, mode="create"):
        if mode == "create":
            params["shopinvader_backend_id"] = self.shopinvader_backend.id
            params["channel_id"] = self.shopinvader_backend.helpdesk_channel_id.id
        return super()._prepare_params(params, mode=mode)


class AttachmentService(Component):
    _name = "attachment.service"
    _inherit = ["attachment.service", "base.shopinvader.service"]
    _collection = "shopinvader.backend"
