# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component


class TicketService(Component):
    _inherit = "helpdesk.ticket.service"

    @restapi.method(
        routes=[(["/<int:id>/request_return"], "POST")],
        input_param={},
        output_param=restapi.Datamodel("helpdesk.ticket.output"),
    )
    def request_return(self, _ticket_id):
        ticket = self._get(_ticket_id)
        ticket.return_sale_lines()
        if len(ticket.return_picking_ids) == 1:
            ticket.return_picking_ids.button_validate()
        return self._return_record(ticket)
