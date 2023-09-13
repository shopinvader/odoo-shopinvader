# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from typing import List

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.mail_message import MailMessageInfo, MailMessageRequest
from ..pydantic_models.ticket import (
    HelpdeskTicketInfo,
    HelpdeskTicketRequest,
    HelpdeskTicketSaleLineRequest,
)

_logger = logging.getLogger(__name__)


class TicketService(Component):
    """Shopinvader service to manage helpdesk tickets."""

    _name = "helpdesk.ticket.service"
    _inherit = [
        "base.helpdesk.rest.service",
        "base.shopinvader.service",
        "rest.attachment.service.mixin",
    ]
    _usage = "helpdesk_ticket"
    _expose_model = "helpdesk.ticket"
    _description = __doc__
    _collection = "shopinvader.backend"

    @restapi.method(
        routes=[(["/<int:id>"], "GET")],
        input_param={},
        output_param=PydanticModel(HelpdeskTicketInfo),
    )
    def get(self, _id):
        record = self.env[self._expose_model].browse(self._get(_id).id)
        return HelpdeskTicketInfo.from_rec(record)

    @restapi.method(
        routes=[(["/"], "GET")],
        input_param={},
        output_param=PydanticModelList(HelpdeskTicketInfo),
    )
    def search(self):
        domain = self._get_base_search_domain()
        result: List[HelpdeskTicketInfo] = []
        for item in self.env[self._expose_model].search(domain):
            result.append(HelpdeskTicketInfo.from_rec(item))
        return result

    @restapi.method(
        routes=[(["/create"], "POST")],
        input_param=PydanticModel(HelpdeskTicketRequest),
        output_param=PydanticModel(HelpdeskTicketInfo),
    )
    # pylint: disable=W8106
    def create(self, ticket: HelpdeskTicketRequest) -> HelpdeskTicketInfo:
        vals = self._prepare_params(ticket.dict(), mode="create")
        record = self.env[self._expose_model].create(vals)
        if "partner_id" in vals:
            vals.update(
                record.play_onchanges(
                    vals,
                    [
                        "partner_id",
                    ],
                )
            )
            record.write(vals)
        return HelpdeskTicketInfo.from_rec(record)

    @restapi.method(
        routes=[(["/<int:id>"], "DELETE")],
        output_param={},
    )
    def cancel(self, _id):
        stage_cancelled = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_cancelled")
        record = self._get(_id)
        record.stage_id = stage_cancelled
        return {}

    def _params_to_prepare_by_appending_id(self):
        return ["category", "team", "sale"]

    def _prepare_params(self, params, mode="create"):
        if mode == "create":
            if params.get("partner"):
                partner = params.pop("partner")
                params["partner_name"] = partner.pop("name")
                params["partner_email"] = partner.pop("email")
                if "lang" in partner:
                    params["partner_lang"] = partner.pop("lang")

            elif self.partner:
                params["partner_id"] = self.partner.id
                params.pop("partner", None)
            else:
                raise UserError(_("The partner is mandatory"))

            params["shopinvader_backend_id"] = self.shopinvader_backend.id
            params["channel_id"] = self.shopinvader_backend.helpdesk_channel_id.id

        for key in self._params_to_prepare_by_appending_id():
            val = params.pop(key)
            if val and "id" in val:
                params["%s_id" % key] = val["id"]
        return params

    def _get_base_search_domain(self):
        res = super()._get_base_search_domain()
        res += [("partner_id", "=", self.partner.id)]
        return res

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
        return HelpdeskTicketInfo.from_rec(ticket)

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
        return HelpdeskTicketInfo.from_rec(ticket)

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
        return HelpdeskTicketInfo.from_rec(ticket)

    def _find_helpdesk_ticket_sale_line(self, ticket, sale_line):
        ticket_sale_line = ticket.mapped("sale_line_ids").filtered(
            lambda l: l.sale_line_id == sale_line
        )
        return ticket_sale_line

    @restapi.method(
        routes=[(["/<int:id>/message_post"], "POST")],
        input_param=PydanticModel(MailMessageRequest),
        output_param=PydanticModel(MailMessageInfo),
    )
    def message_post(self, _id, message):
        record = self._get(_id)
        kwargs = self._prepare_message_post_params(message.dict())
        message = record.message_post(**kwargs)
        return MailMessageInfo.from_rec(message)

    def _prepare_message_post_params(self, params):
        params["author_id"] = self.partner.id
        params["message_type"] = "comment"
        params["subtype_id"] = self.env["ir.model.data"]._xmlid_to_res_id(
            "mail.mt_comment"
        )
        attachments = params.pop("attachments", False)
        if attachments:
            params["attachment_ids"] = [item["id"] for item in attachments]
        return params
