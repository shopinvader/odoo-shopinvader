# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if


class ResPartnerEventListener(Component):
    _name = "res.partner.event.listener"
    _inherit = "base.event.listener"
    _apply_on = ["res.partner"]

    @skip_if(lambda self, record, backends: self._skip_it(record, backends))
    def on_shopinvader_validate(self, record, backends):
        self._notify_address_validate(record, backends)

    def _skip_it(self, record, backends):
        return not backends or record.address_type != "address"

    def _notify_address_validate(self, partner, backends):
        """Notify address' owner."""
        notif_type = "address_validated"
        recipient = partner.parent_id
        for backend in backends:
            # Send shopinvader notification
            backend._send_notification(notif_type, recipient)
        name = partner.name or partner.contact_address.replace("\n", " | ")
        msg_body = _("Shop {addr_type} '{name}' validated").format(
            addr_type=partner.addr_type_display().lower(), name=name
        )
        recipient.message_post(body=msg_body)
