# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.ticket import (
    HelpdeskTicketInfo,
    HelpdeskTicketRequest,
    HelpdeskTicketSaleLineRequest,
)


class TicketService(Component):
    """Shopinvader service to manage helpdesk tickets."""

    _name = "helpdesk.ticket.service"
    _inherit = ["helpdesk.ticket.service", "base.shopinvader.service"]
    _collection = "shopinvader.backend"

    @restapi.method(
        routes=[(["/<int:id>"], "GET")],
        input_param={},
        output_param=PydanticModel(HelpdeskTicketInfo),
    )
    def get(self, _id):
        # TODO: Find a better way to extend the PydanticModel returned
        record = self.env[self._expose_model].browse(super().get(_id).id)
        return HelpdeskTicketInfo.from_orm(record)

    @restapi.method(
        routes=[(["/"], "GET")],
        input_param={},
        output_param=PydanticModelList(HelpdeskTicketInfo),
    )
    def search(self):
        infos = [
            HelpdeskTicketInfo.from_orm(self.env[self._expose_model].browse(item.id))
            for item in super().search()
        ]
        return infos

    @restapi.method(
        routes=[(["/create"], "POST")],
        input_param=PydanticModel(HelpdeskTicketRequest),
        output_param=PydanticModel(HelpdeskTicketInfo),
    )
    # pylint: disable=W8106
    def create(self, ticket: HelpdeskTicketRequest) -> HelpdeskTicketInfo:
        record = self.env[self._expose_model].browse(super().create(ticket).id)
        return HelpdeskTicketInfo.from_orm(record)

    def _params_to_prepare_by_appending_id(self):
        res = super()._params_to_prepare_by_appending_id()
        res.append("sale")
        return res

    def _prepare_params(self, params, mode="create"):
        if mode == "create":
            params["shopinvader_backend_id"] = self.shopinvader_backend.id
            params["channel_id"] = self.shopinvader_backend.helpdesk_channel_id.id
        params = super()._prepare_params(params, mode=mode)
        return params

    @restapi.method(
        routes=[(["/<int:id>/add_sale_line"], "POST")],
        input_param=PydanticModel(HelpdeskTicketSaleLineRequest),
        output_param=PydanticModel(HelpdeskTicketInfo),
    )
    def add_sale_line(self, _ticket_id, line):
        ticket = self._get(_ticket_id)
        sale_line = self.env["sale.order.line"].browse(line.sale_line_id)
        existing_item = self._find_helpdesk_ticket_sale_line(ticket, sale_line)
        if existing_item:
            existing_item.qty = line.qty
        else:
            self.env["helpdesk.ticket.sale.line"].create(
                {"ticket_id": ticket.id, "sale_line_id": sale_line.id, "qty": line.qty}
            )
        return HelpdeskTicketInfo.from_orm(ticket)

    @restapi.method(
        routes=[(["/<int:id>/update_sale_line"], "POST")],
        input_param=PydanticModel(HelpdeskTicketSaleLineRequest),
        output_param=PydanticModel(HelpdeskTicketInfo),
    )
    def update_sale_line(self, _ticket_id, line):
        ticket = self._get(_ticket_id)
        sale_line = self.env["sale.order.line"].browse(line.sale_line_id)
        existing_item = self._find_helpdesk_ticket_sale_line(ticket, sale_line)
        if not existing_item:
            raise UserError(
                _("The targeted sale line does not already exist on this ticket.")
            )
        existing_item.qty = line.qty
        return HelpdeskTicketInfo.from_orm(ticket)

    @restapi.method(
        routes=[(["/<int:id>/delete_sale_line"], "POST")],
        input_param=PydanticModel(HelpdeskTicketSaleLineRequest),
        output_param=PydanticModel(HelpdeskTicketInfo),
    )
    def delete_sale_line(self, _ticket_id, line):
        ticket = self._get(_ticket_id)
        sale_line = self.env["sale.order.line"].browse(line.sale_line_id)
        ticket_sale_line = self._find_helpdesk_ticket_sale_line(ticket, sale_line)
        ticket_sale_line.unlink()
        return HelpdeskTicketInfo.from_orm(ticket)

    def _find_helpdesk_ticket_sale_line(self, ticket, sale_line):
        ticket_sale_line = ticket.mapped("sale_line_ids").filtered(
            lambda l: l.sale_line_id == sale_line
        )
        return ticket_sale_line
