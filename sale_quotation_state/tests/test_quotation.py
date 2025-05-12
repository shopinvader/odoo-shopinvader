# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestQuotation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        product = cls.env["product.product"].create({"name": "Test Product"})
        partner = cls.env["res.partner"].create({"name": "John"})
        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [(0, 0, {"product_id": product.id})],
            }
        )

    def test_create_quotation(self):
        self.assertEqual(self.so.quotation_state, "draft")

    def test_request_quotation(self):
        self.so.typology = "cart"
        self.so.action_request_quotation()
        self.assertEqual(self.so.quotation_state, "customer_request")

    def test_send_requested_quotation(self):
        self.so.typology = "cart"
        self.so.action_request_quotation()
        self.so.action_quotation_sent()
        self.assertEqual(self.so.quotation_state, "waiting_acceptation")

    def test_send_draft_quotation(self):
        self.so.action_quotation_sent()
        self.assertEqual(self.so.quotation_state, "waiting_acceptation")

    def test_confirm_quotation(self):
        self.so.action_quotation_sent()
        self.so.action_confirm_quotation()
        self.assertEqual(self.so.quotation_state, "accepted")

    def test_not_allowed_confirm_quotation(self):
        with self.assertRaises(UserError) as cm:
            self.so.action_confirm_quotation()
        self.assertIn("Only quotation with the state", cm.exception.args[0])
