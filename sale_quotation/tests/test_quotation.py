# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
from odoo.tests.common import TransactionCase

from ..exceptions import InvalidQuotationStateError


class TestQuotation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
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
        self.so.action_customer_request_quotation()
        self.so.action_quotation_sent()
        self.assertEqual(self.so.quotation_state, "waiting_acceptation")

    def test_confirm_quotation(self):
        self.so.action_customer_request_quotation()
        self.so.action_quotation_sent()
        self.so.action_customer_accept_quotation()
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
        self.env["sale.order.confirm.warning.wizard"].create(
            {
                "sale_order_ids": [Command.link(self.so.id)],
            }
        ).confirm_and_proceed()
        self.assertEqual(self.so.quotation_state, "accepted")
        self.assertEqual(self.so.typology, "sale")

    def test_convert_to_draft_resets_typology(self):
        self.so.action_customer_request_quotation()
        self.so.action_quotation_sent()
        self.so.action_confirm()
        self.so.action_cancel()
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

    def test_action_customer_workflow(self):
        """Test that the customer workflow actions are working as expected."""
        ########################
        # quotation state: draft
        ########################

        self.assertEqual(self.so.quotation_state, "draft")
        with self.assertRaises(InvalidQuotationStateError):
            self.so.action_customer_accept_quotation()

        with self.assertRaises(InvalidQuotationStateError):
            self.so.action_customer_reset_quotation_to_draft()

        with self.assertRaises(InvalidQuotationStateError):
            self.so.action_customer_cancel_quotation()

        # in draft state we can:
        self.so.action_customer_request_quotation()
        self.assertEqual(self.so.quotation_state, "customer_request")

        ###################################
        # quotation state: customer_request
        ###################################

        with self.assertRaises(InvalidQuotationStateError):
            self.so.action_customer_accept_quotation()

        # in customer_request state we can reset to draft:
        self.so.action_customer_reset_quotation_to_draft()
        self.assertEqual(self.so.quotation_state, "draft")
        self.assertEqual(self.so.typology, "quote")

        # set in customer_request state again:
        self.so.action_customer_request_quotation()
        self.assertEqual(self.so.quotation_state, "customer_request")

        # in customer_request state we can cancel:
        self.so.action_customer_cancel_quotation()
        self.assertEqual(self.so.quotation_state, "cancel")
        self.assertEqual(self.so.typology, "quote")
        self.assertEqual(self.so.state, "cancel")

        # set in customer_request state again:
        self.so.action_customer_reset_quotation_to_draft()
        self.so.action_customer_request_quotation()
        self.assertEqual(self.so.quotation_state, "customer_request")

        # customer_request state we can send to client:
        self.so.action_quotation_sent()
        self.assertEqual(self.so.quotation_state, "waiting_acceptation")
        self.assertEqual(self.so.state, "sent")

        ######################################
        # quotation state: waiting_acceptation
        ######################################
        with self.assertRaises(InvalidQuotationStateError):
            self.so.action_quotation_sent()

        # in waiting_acceptation state customer can accept the quotation:
        self.so.action_customer_accept_quotation()
        self.assertEqual(self.so.quotation_state, "accepted")
        self.assertEqual(self.so.typology, "sale")

        # reset to waiting_acceptation state:
        self.so.with_context(disable_cancel_warning=True).action_cancel()
        self.so.action_customer_reset_quotation_to_draft()
        self.so.action_customer_request_quotation()
        self.so.action_quotation_sent()
        self.assertEqual(self.so.quotation_state, "waiting_acceptation")
        self.assertEqual(self.so.typology, "quote")

        # in waiting_acceptation state customer can reset to draft:
        self.so.action_customer_reset_quotation_to_draft()
        self.assertEqual(self.so.quotation_state, "draft")

        # reset to waiting_acceptation state again:
        self.so.action_customer_request_quotation()
        self.so.action_quotation_sent()
        self.assertEqual(self.so.quotation_state, "waiting_acceptation")

        # in waiting_acceptation state customer can cancel the quotation:
        self.so.action_customer_cancel_quotation()
        self.assertEqual(self.so.quotation_state, "cancel")
        self.assertEqual(self.so.typology, "quote")

        #########################
        # quotation state: cancel
        #########################
        with self.assertRaises(InvalidQuotationStateError):
            self.so.action_customer_accept_quotation()
        with self.assertRaises(InvalidQuotationStateError):
            self.so.action_customer_request_quotation()
        with self.assertRaises(InvalidQuotationStateError):
            self.so.action_customer_cancel_quotation()

        # in cancel state we can reset to draft:
        self.so.action_customer_reset_quotation_to_draft()
        self.assertEqual(self.so.quotation_state, "draft")
        self.assertEqual(self.so.typology, "quote")
