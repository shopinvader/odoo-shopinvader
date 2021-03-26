# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if


class ShopinvaderPartnerEventListener(Component):
    _name = "shopinvader.partner.event.listener"
    _inherit = "base.event.listener"

    _apply_on = ["shopinvader.partner"]

    @skip_if(lambda self, record: self._skip_it(record))
    def on_shopinvader_validate(self, record):
        self._notify_customer_validate(record)

    def _skip_it(self, record):
        return self.env.context.get("_bypass_validate_notification")

    def _notify_customer_validate(self, invader_partner):
        """Notify real res.partner based on its type."""
        partner = invader_partner.record_id
        # TODO: handle other states?
        if invader_partner.state == "active":
            notif_type = "customer_validated"
            # Send shopinvader notification
            invader_partner.backend_id._send_notification(notif_type, partner)
            name = partner.name or partner.contact_address.replace("\n", " | ")
            msg_body = _("Shop {addr_type} '{name}' validated").format(
                addr_type=partner.addr_type_display().lower(), name=name
            )
            partner.message_post(body=msg_body)
