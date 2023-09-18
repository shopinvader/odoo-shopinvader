# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError

from odoo.addons.shopinvader_restapi.tests.common import CommonCase


class TestMembershipService(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.membership_line_obj = cls.env["membership.membership_line"]
        cls.product_obj = cls.env["product.product"]
        cls.partner = cls.env.ref("shopinvader_restapi.partner_1")
        str_today = fields.Date.today()
        cls.date_today = fields.Date.from_string(str_today)
        cls.next_month = fields.Date.to_string(cls.date_today + timedelta(days=30))
        cls.product = cls.product_obj.create(
            {
                "type": "service",
                "name": "Membership Test Product",
                "membership": True,
                "membership_date_from": cls.date_today,
                "membership_date_to": cls.next_month,
                "list_price": 100.00,
            }
        )

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        with self.work_on_services(partner=self.partner) as work:
            self.service = work.component(usage="membership")
        with self.work_on_services(partner=self.backend.anonymous_partner_id) as work:
            self.service_guest = work.component(usage="membership")

    def _check_data_content(self, data, membership_lines):
        """
        Check data based on given membership lines
        :param data: list
        :param membership_lines: membership.membership_line recordset
        :return: bool
        """
        # To have them into correct order
        service = self.service
        membership_lines = membership_lines.search(service._get_base_search_domain())
        self.assertEqual(len(data), len(membership_lines))
        dts = fields.Date.to_string
        for current_data, membership_line in zip(data, membership_lines):
            state_label = service._get_selection_label(membership_line, "state")
            self.assertEqual(current_data.get("membership_line_id"), membership_line.id)
            self.assertEqual(
                current_data.get("date") or False, dts(membership_line.date)
            )
            self.assertEqual(
                current_data.get("date_from") or False,
                dts(membership_line.date_from),
            )
            self.assertEqual(
                current_data.get("date_to") or False, dts(membership_line.date_to)
            )
            self.assertEqual(
                current_data.get("date_cancel") or False,
                dts(membership_line.date_cancel),
            )
            self.assertEqual(
                current_data.get("membership_id").get("id"),
                membership_line.membership_id.id,
            )
            self.assertEqual(
                current_data.get("membership_id").get("name"),
                membership_line.membership_id.name,
            )
            self.assertEqual(
                current_data.get("member_price"), membership_line.member_price
            )
            self.assertEqual(current_data.get("state").get("label"), state_label)
            self.assertEqual(
                current_data.get("state").get("value"), membership_line.state
            )
        return True

    def test_get_membership_lines_logged(self):
        # Check first without membership related to the partner
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self.assertFalse(data)
        # Then create a membership related to partner
        invoice = self.partner.create_membership_invoice(
            self.product, self.product.list_price
        )
        membership_line = self.membership_line_obj.search(
            [("account_invoice_line", "=", invoice.invoice_line_ids.id)], limit=1
        )
        self.assertEqual(membership_line.partner, self.service.partner)
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self._check_data_content(data, membership_line)

    def test_get_multi_membership_lines(self):
        invoice1 = self.partner.create_membership_invoice(
            self.product, self.product.list_price
        )
        invoice2 = self.partner.create_membership_invoice(
            self.product, self.product.list_price
        )
        invoice3 = self.partner.create_membership_invoice(
            self.product, self.product.list_price
        )
        membership_line_1 = self.membership_line_obj.search(
            [("account_invoice_line", "=", invoice1.invoice_line_ids.id)], limit=1
        )
        membership_line_2 = self.membership_line_obj.search(
            [("account_invoice_line", "=", invoice2.invoice_line_ids.id)], limit=1
        )
        membership_line_3 = self.membership_line_obj.search(
            [("account_invoice_line", "=", invoice3.invoice_line_ids.id)], limit=1
        )
        membership_line_2.write(
            {
                "member_price": 22,
                "date_from": self.date_today,
                "date_to": self.next_month,
            }
        )
        membership_line_3.write(
            {
                "date": self.date_today,
                "date_cancel": self.next_month,
            }
        )
        service_partner = self.service.partner
        membership_lines = membership_line_1 | membership_line_2 | membership_line_3
        self.assertEqual(membership_line_1.partner, service_partner)
        self.assertEqual(membership_line_2.partner, service_partner)
        self.assertEqual(membership_line_3.partner, service_partner)
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self._check_data_content(data, membership_lines)

    def test_subscription(self):
        # Check first not logged
        with self.assertRaises(UserError) as e:
            self.service_guest.dispatch("subscribe", self.product.id)
        self.assertEqual(e.exception.args[0], "A user should be logged")
        # Then with a logged user but with a non membership product
        self.product.write({"membership": False})
        with self.assertRaises(UserError) as e:
            self.service.dispatch("subscribe", self.product.id)
        self.assertIn("No membership product found with", e.exception.args[0])
        # Then user logged and real membership product
        self.product.write({"membership": True})
        result = self.service.dispatch("subscribe", self.product.id)
        invoice_id = result.get("invoice_id")
        invoice = self.env["account.move"].browse(invoice_id)
        self.assertEqual(self.partner, invoice.partner_id)
        self.assertEqual(self.product, invoice.invoice_line_ids[0].product_id)
        self.assertEqual(
            self.product.list_price, invoice.invoice_line_ids[0].price_unit
        )
