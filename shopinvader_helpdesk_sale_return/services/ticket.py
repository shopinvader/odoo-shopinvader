# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel
from odoo.addons.component.core import Component
from odoo.addons.shopinvader_helpdesk.pydantic_models.ticket import HelpdeskTicketInfo


class TicketService(Component):
    _inherit = "helpdesk.ticket.service"

    @restapi.method(
        routes=[(["/<int:id>/request_return"], "POST")],
        input_param={},
        output_param=PydanticModel(HelpdeskTicketInfo),
    )
    def request_return(self, _ticket_id):
        ticket = self._get(_ticket_id)
        ticket.return_sale_lines()
        if (
            len(ticket.return_picking_ids) == 1
            and ticket.category_id.automatically_generate_return_for
        ):
            picking = ticket.return_picking_ids
            picking.carrier_id = ticket.category_id.automatically_generate_return_for
            picking._put_in_pack(picking.move_line_ids)
            picking.print_return_label()
            label = self.env["shipping.label"].search(
                [("res_model", "=", "stock.picking"), ("res_id", "=", picking.id)]
            )
            label.copy(default={"res_model": "helpdesk.ticket", "res_id": ticket.id})
        return HelpdeskTicketInfo.from_orm(ticket)
