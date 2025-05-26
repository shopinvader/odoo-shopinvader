# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestQuotation(TransactionCase):
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

    def test_request_quotation(self):
        self.so.typology = "cart"
        self.so.action_request_quotation()
        self.assertEqual(self.so.quotation_state, "customer_request")

    def test_send_requested_quotation(self):
        self.so.typology = "cart"
        self.so.action_request_quotation()
        self.so.action_quotation_sent()
        self.assertEqual(self.so.quotation_state, "waiting_acceptation")
