# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
import pathlib
import unittest

from werkzeug.datastructures import FileStorage

from odoo.addons.component.tests.common import TransactionComponentCase
from odoo.addons.extendable.tests.common import ExtendableMixin
from odoo.addons.shopinvader_restapi.tests.common import CommonCase


class AttachmentCommonCase(unittest.TestCase):
    def create_attachment(self, record_id, params=None):
        attrs = {"object_id": record_id, "params": "{}"}
        res = None
        if params:
            attrs["params"] = json.dumps(params)
        with open(pathlib.Path(__file__).resolve()) as fp:
            attrs["file"] = FileStorage(fp)
            res = self.service.dispatch("create_attachment", params=attrs)
        return res


class HelpdeskTicketCommonCase(CommonCase, TransactionComponentCase, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.init_extendable_registry()

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner = self.env.ref("shopinvader_restapi.partner_1")
        with self.work_on_services(
            partner=self.partner,
        ) as work:
            self.service = work.component(usage="helpdesk_ticket")

    @classmethod
    def tearDownClass(cls):
        cls.reset_extendable_registry()
        super().tearDownClass()

    def generate_ticket_data(self, partner=None):
        data = {
            "description": "My order is late",
            "name": "order num 4",
            "category": {"id": self.ref("helpdesk_mgmt.helpdesk_category_3")},
        }
        if partner:
            data["partner"] = partner
        return data

    def assert_ticket_ok(self, ticket):
        self.assertEqual(len(ticket), 1)
        self.assertEqual(ticket.category_id.name, "Odoo")


class HelpdeskTicketNoaccountCase(HelpdeskTicketCommonCase, AttachmentCommonCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        with self.work_on_services(
            partner=None,
        ) as work:
            self.service = work.component(usage="helpdesk_ticket")

    def test_create_ticket_noaccount(self):
        data = self.generate_ticket_data(
            partner={
                "email": "customer+testststs@example.org",
                "name": "Customer",
            }
        )
        self.service.dispatch("create", params=data)
        ticket = self.env["helpdesk.ticket"].search(
            [("partner_email", "=", "customer+testststs@example.org")]
        )
        self.assert_ticket_ok(ticket)
        # self.assertEqual(ticket.partner_id.e  mail, ticket.partner_email)

    def test_create_ticket_noaccount_attachment(self):
        data = self.generate_ticket_data(
            partner={
                "email": "customer+testststs@example.org",
                "name": "Customer",
            }
        )
        res = self.service.dispatch("create", params=data)
        self.assertEqual(len(res["attachments"]), 0)
        attachment_res = self.create_attachment(res["id"])
        ticket = self.env["helpdesk.ticket"].search(
            [("partner_email", "=", "customer+testststs@example.org")]
        )
        self.assert_ticket_ok(ticket)
        self.assertEqual(ticket.attachment_ids.id, attachment_res["id"])
        # self.assertEqual(ticket.partner_id.email, ticket.partner_email)


class HelpdeskTicketAuthenticatedCase(HelpdeskTicketCommonCase, AttachmentCommonCase):
    def test_create_ticket_account_attachment(self):
        data = self.generate_ticket_data()
        res = self.service.dispatch("create", params=data)
        attachment_res = self.create_attachment(res["id"])
        ticket = self.env["helpdesk.ticket"].search([("id", "=", res["id"])])
        self.assert_ticket_ok(ticket)
        self.assertEqual(ticket.attachment_ids.id, attachment_res["id"])

    def test_ticket_message(self):
        data = self.generate_ticket_data()
        res = self.service.dispatch("create", params=data)
        ticket = self.env["helpdesk.ticket"].search([("id", "=", res["id"])])
        self.assert_ticket_ok(ticket)
        message_data = {"body": "Also here is a picture"}
        self.service.dispatch("message_post", ticket.id, params=message_data)
        self.assertEqual(len(ticket.message_ids), 2)  # There is a technical message

    def test_partner_infos(self):
        data = self.generate_ticket_data()
        res = self.service.dispatch("create", params=data)
        ticket = self.env["helpdesk.ticket"].search([("id", "=", res["id"])])
        self.assert_ticket_ok(ticket)

        self.assertEqual(ticket.partner_id, self.partner)
        self.assertEqual(ticket.partner_email, self.partner.email)
        self.assertEqual(ticket.partner_name, self.partner.name)


class HelpdeskTicketSaleCase(HelpdeskTicketCommonCase):
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
