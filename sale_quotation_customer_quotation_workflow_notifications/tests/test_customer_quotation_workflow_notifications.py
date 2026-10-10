# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestCustomerQuotationWorkflowNotifications(TransactionCase):
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

        cls.mt_quotation_request = cls.env.ref(
            "sale_quotation_customer_quotation_workflow_notifications.mt_quotation_request"
        )
        cls.mt_customer_accept_quotation = cls.env.ref(
            "sale_quotation_customer_quotation_workflow_notifications.mt_customer_accept_quotation"
        )
        cls.mt_customer_reset_quotation_to_draft = cls.env.ref(
            "sale_quotation_customer_quotation_workflow_notifications.mt_customer_reset_quotation_to_draft"
        )
        cls.mt_customer_cancel_quotation = cls.env.ref(
            "sale_quotation_customer_quotation_workflow_notifications.mt_customer_cancel_quotation"
        )

        # Ensure all custom notifications types are assigned to the salesman
        # when creating an SO
        (
            cls.mt_quotation_request
            | cls.mt_customer_accept_quotation
            | cls.mt_customer_reset_quotation_to_draft
            | cls.mt_customer_cancel_quotation
        ).default = True

        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "use_customer_quotation_workflow": True,
                "user_id": cls.salesman.id,
            }
        )

    def _get_notifications(self, partner):
        """Helper to return the `mail.notification`'s associated to a given partner."""
        return self.env["mail.notification"].search(
            [("res_partner_id", "=", partner.id)]
        )

    def _get_notified_messages(self, sale_order, partner):
        """
        Helper to return the messages of the SO that notified the given partner.

        This method is necessary since the subscription mechanism does not necessarily
        create a `mail.notification` record though partners are still notified.
        """
        return sale_order.message_ids.filtered(
            lambda m: partner in m.notified_partner_ids
        )

    def test_quotation_request_notifications(self):
        """
        Test that when a user requests a quotation:

            - the salesperson gets notified of the quotation request
            - the customer receives a confirmation of the quotation request
        """
        sale_order = self.sale_order
        sale_order.action_customer_request_quotation()

        customer_notifications = self._get_notifications(sale_order.partner_id)
        self.assertEqual(
            len(customer_notifications),
            1,
            "Customer should be notified of successful request",
        )
        self.assertEqual(
            "Quotation Request Confirmation",
            customer_notifications.mail_message_id.subject,
        )

        # Check that a notification was posted for the salesperson
        salesman_messages = self._get_notified_messages(
            sale_order, sale_order.user_id.partner_id
        )
        self.assertEqual(
            len(salesman_messages),
            1,
            "Salesperson should be notified of quotation requests",
        )
        self.assertEqual("Customer Quotation Request", salesman_messages.subject)

    def test_customer_quotation_actions_notify_salesman(self):
        """Test that the different customer actions notify the salesman."""
        sale_order = self.sale_order
        sale_order.action_customer_request_quotation()
        sale_order.action_customer_reset_quotation_to_draft()

        salesman_messages = self._get_notified_messages(
            sale_order, sale_order.user_id.partner_id
        )
        self.assertEqual(
            len(salesman_messages),
            2,
        )
        self.assertIn(
            "Customer Quotation Reset to Draft", salesman_messages.mapped("subject")
        )

        sale_order.action_customer_request_quotation()
        sale_order.action_customer_cancel_quotation()

        salesman_messages = self._get_notified_messages(
            sale_order, sale_order.user_id.partner_id
        )
        self.assertEqual(
            len(salesman_messages),
            4,
        )
        self.assertIn(
            "Customer Quotation Cancelled", salesman_messages.mapped("subject")
        )

        sale_order.action_customer_reset_quotation_to_draft()
        sale_order.action_customer_request_quotation()
        sale_order.action_quotation_sent()
        sale_order.action_customer_accept_quotation()
        salesman_messages = self._get_notified_messages(
            sale_order, sale_order.user_id.partner_id
        )
        self.assertEqual(
            len(salesman_messages),
            7,
        )
        self.assertIn(
            "Customer Quotation Accepted", salesman_messages.mapped("subject")
        )
