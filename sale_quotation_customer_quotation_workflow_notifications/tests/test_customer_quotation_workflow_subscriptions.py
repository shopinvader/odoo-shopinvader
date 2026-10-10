# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestCustomerQuotationWorkflowSubscriptions(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.salesman = cls.env["res.users"].create(
            {
                "name": "Test Sales Man",
                "login": "test_user",
                "email": "test_user@example.com",
                "groups_id": [
                    Command.set([cls.env.ref("sales_team.group_sale_salesman").id])
                ],
            }
        )

        cls.customer = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
                "email": "test_customer@example.com",
            }
        )

        custom_quotation_subtype = cls.env.ref(
            "sale_quotation_customer_quotation_workflow_notifications.mt_customer_quotation",
        )
        cls.customer_quotation_default_message_types = (
            cls.env["mail.message.subtype"]
            .search(
                [
                    ("res_model", "=", "sale.order"),
                    ("parent_id", "=", custom_quotation_subtype.id),
                ]
            )
            .filtered("default")
        )

        cls.base_default_message_types = (
            cls.env["mail.message.subtype"]
            .search(
                [
                    ("res_model", "in", [False, "sale.order"]),
                    ("parent_id", "!=", custom_quotation_subtype.id),
                ]
            )
            .filtered("default")
        )

    def _get_salesman_notification_types(self, so):
        """Helper to retrieve the notifications subtypes of the salesman for.

        a given SO.
        """
        salesperson_follower = so.message_follower_ids.filtered(
            lambda f: f.partner_id == so.user_id.partner_id
        )
        return salesperson_follower.subtype_ids

    def test_create_base_worflow_subscriptions(self):
        """Test that the salesman is subscribed to default normal subtypes.

        when creating an SO using normal workflow.
        """
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "use_customer_quotation_workflow": False,
                "user_id": self.salesman.id,
            }
        )
        self.assertEqual(
            self._get_salesman_notification_types(sale_order),
            self.base_default_message_types,
        )

    def test_create_customer_quotation_worflow_subscriptions(self):
        """Test that the salesman is subscribed to custom default subtypes.

        when creating an SO using normal workflow.
        """
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "use_customer_quotation_workflow": True,
                "user_id": self.salesman.id,
            }
        )

        self.assertEqual(
            self._get_salesman_notification_types(sale_order),
            self.customer_quotation_default_message_types,
        )

    def test_toggle_customer_quotation_workflow_subscriptions(self):
        """Test that the salesman is subscribed to the default message types.

        from the corresponding workfow when toggling the "Customer Quotation" workflow.
        """
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "use_customer_quotation_workflow": False,
                "user_id": self.salesman.id,
            }
        )
        self.assertEqual(
            self._get_salesman_notification_types(sale_order),
            self.base_default_message_types,
        )

        sale_order.use_customer_quotation_workflow = True
        self.assertEqual(
            self._get_salesman_notification_types(sale_order),
            self.customer_quotation_default_message_types,
        )
        sale_order.use_customer_quotation_workflow = False
        self.assertEqual(
            self._get_salesman_notification_types(sale_order),
            self.base_default_message_types,
        )
