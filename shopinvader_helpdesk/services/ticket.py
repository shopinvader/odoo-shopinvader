# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _
from odoo.exceptions import UserError

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component
from odoo.addons.datamodel import fields
from odoo.addons.datamodel.core import Datamodel


class HelpdeskTicketSaleLineInput(Datamodel):
    _name = "helpdesk.ticket.sale.line.input"

    sale_line_id = fields.Integer(required=True, allow_none=False)
    qty = fields.Integer(required=False, allow_none=False)


class HelpdeskTicketSaleLineOutput(Datamodel):
    _name = "helpdesk.ticket.sale.line.output"

    sale_line_id = fields.Integer(required=True, allow_none=False)
    qty = fields.Float(required=True, allow_none=False)
    product_name = fields.String()


class HelpdeskTicketOutput(Datamodel):
    _name = "helpdesk.ticket.output"
    _inherit = "helpdesk.ticket.output"

    sale_lines = fields.NestedModel(
        "helpdesk.ticket.sale.line.output", required=False, allow_none=False, many=True
    )


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

    def _json_parser(self):
        res = super()._json_parser()
        res += [("sale_line_ids:sale_lines", ["sale_line_id", "product_name", "qty"])]
        return res

    @restapi.method(
        routes=[(["/<int:id>/add_sale_line"], "POST")],
        input_param=restapi.Datamodel("helpdesk.ticket.sale.line.input"),
        output_param=restapi.Datamodel("helpdesk.ticket.output"),
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
        return self._return_record(ticket)

    @restapi.method(
        routes=[(["/<int:id>/update_sale_line"], "POST")],
        input_param=restapi.Datamodel("helpdesk.ticket.sale.line.input"),
        output_param=restapi.Datamodel("helpdesk.ticket.output"),
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
        return self._return_record(ticket)

    @restapi.method(
        routes=[(["/<int:id>/delete_sale_line"], "POST")],
        input_param=restapi.Datamodel("helpdesk.ticket.sale.line.input"),
        output_param=restapi.Datamodel("helpdesk.ticket.output"),
    )
    def delete_sale_line(self, _ticket_id, line):
        ticket = self._get(_ticket_id)
        sale_line = self.env["sale.order.line"].browse(line.sale_line_id)
        ticket_sale_line = self._find_helpdesk_ticket_sale_line(ticket, sale_line)
        ticket_sale_line.unlink()
        return self._return_record(ticket)

    def _find_helpdesk_ticket_sale_line(self, ticket, sale_line):
        ticket_sale_line = ticket.mapped("sale_line_ids").filtered(
            lambda l: l.sale_line_id == sale_line
        )
        return ticket_sale_line
