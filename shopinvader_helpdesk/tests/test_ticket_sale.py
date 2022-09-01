# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.tests.common import SavepointComponentCase
from odoo.addons.extendable.tests.common import ExtendableMixin
from odoo.addons.shopinvader.tests.common import CommonCase


class HelpdeskTicketSaleCase(CommonCase, SavepointComponentCase, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setUpExtendable()

    def setUp(self, *args, **kwargs):
        ExtendableMixin.setUp(self)
        super().setUp(*args, **kwargs)
        self.env.context["authenticated_partner_id"] = self.env.ref(
            "shopinvader.partner_1"
        ).id
        with self.work_on_services(
            partner=self.env.ref("shopinvader.partner_1"),
        ) as work:
            self.service = work.component(usage="helpdesk_ticket")

    def generate_ticket_data(self):
        return {
            "description": "My order is late",
            "name": "order num 4",
        }

    def test_ticket_sale(self):
        data = self.generate_ticket_data()
        res = self.service.dispatch("create", params=data)
        ticket = self.env["helpdesk.ticket"].browse(res["id"])
        self.assertEqual(len(ticket.sale_line_ids), 0)
        data = {"sale_line_id": self.env.ref("sale.sale_order_line_1").id, "qty": 2}
        res = self.service.dispatch("add_sale_line", ticket.id, params=data)
        self.assertEqual(len(ticket.sale_line_ids), 1)
        self.assertEqual(ticket.sale_line_ids.qty, 2)
        data["qty"] = 1
        res = self.service.dispatch("update_sale_line", ticket.id, params=data)
        self.assertEqual(len(ticket.sale_line_ids), 1)
        self.assertEqual(ticket.sale_line_ids.qty, 1)
        data["qty"] = 3
        res = self.service.dispatch("add_sale_line", ticket.id, params=data)
        self.assertEqual(len(ticket.sale_line_ids), 1)
        self.assertEqual(ticket.sale_line_ids.qty, 3)
        data = {"sale_line_id": self.env.ref("sale.sale_order_line_2").id, "qty": 2}
        res = self.service.dispatch("add_sale_line", ticket.id, params=data)
        self.assertEqual(len(ticket.sale_line_ids), 2)
        res = self.service.dispatch("delete_sale_line", ticket.id, params=data)
        self.assertEqual(len(ticket.sale_line_ids), 1)
