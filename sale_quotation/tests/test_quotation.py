# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestQuotation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product = cls.env["product.product"].create({"name": "Test Product"})
        cls.partner = cls.env["res.partner"].create({"name": "John"})
        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [Command.create({"product_id": cls.product.id})],
                "use_customer_quotation_workflow": True,
            }
        )

    def test_create_quotation(self):
        self.assertEqual(self.so.quotation_state, "draft")
        self.assertEqual(self.so.typology, "quote")

    def test_send_draft_quotation(self):
        self.so.action_quotation_sent()
        self.assertEqual(self.so.quotation_state, "waiting_acceptation")

    def test_confirm_quotation(self):
        self.so.action_quotation_sent()
        self.so.action_confirm_quotation()
        self.assertEqual(self.so.quotation_state, "accepted")
        self.assertEqual(self.so.typology, "sale")

    def test_not_allowed_confirm_quotation(self):
        action = self.so.with_context(
            use_quotation_confirm_wizard=True
        ).action_confirm()
        self.assertIsInstance(action, dict)
        self.assertEqual(action.get("res_model"), "sale.order.confirm.warning.wizard")
        self.assertEqual(action.get("type"), "ir.actions.act_window")
        self.assertIn("default_message", action.get("context", {}))
        self.assertIn(
            "not in 'Waiting Acceptation'", action["context"]["default_message"]
        )

    def test_convert_to_draft_resets_typology(self):
        self.so.action_quotation_sent()
        self.so.action_confirm()
        self.so.action_draft()
        self.assertEqual(self.so.typology, "quote")

    def test_normal_so_workflow_not_broken(self):
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [Command.create({"product_id": self.product.id})],
            }
        )
        self.assertEqual(so.state, "draft")

        so.action_confirm()
        self.assertEqual(so.state, "sale")

    def test_unable_to_change_workflow_when_confirmed(self):
        so = self.so
        self.assertEqual(so.state, "draft")

        so.action_confirm()
        self.assertEqual(so.state, "sale")
        with self.assertRaises(UserError):
            so.action_toggle_customer_quotation_workflow()
