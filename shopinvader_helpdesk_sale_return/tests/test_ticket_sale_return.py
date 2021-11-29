# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_helpdesk.tests.test_ticket_sale import (
    HelpdeskTicketSaleCase,
)


class HelpdeskTicketSaleReturnCase(HelpdeskTicketSaleCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

    def generate_ticket_data(self):
        return {
            "description": "My order is late",
            "name": "order num 4",
        }

    def test_ticket_sale_return(self):
        data = self.generate_ticket_data()
        res = self.service.dispatch("create", params=data)
        ticket = self.env["helpdesk.ticket"].browse(res["id"])
        data = {
            "sale_line_id": self.env.ref("sale_stock.sale_order_line_42").id,
            "qty": 2,
        }
        res = self.service.dispatch("add_sale_line", ticket.id, params=data)
        data = {"sale_line_id": self.env.ref("sale_stock.sale_order_line_43").id}
        res = self.service.dispatch("add_sale_line", ticket.id, params=data)
        self.assertEqual(len(ticket.sale_line_ids), 2)
        res = self.service.dispatch("request_return", ticket.id, params={})
        self.assertEqual(len(ticket.return_picking_ids), 1)
        self.assertEqual(ticket.return_picking_ids.state, "done")
