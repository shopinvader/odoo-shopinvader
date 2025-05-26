# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import ValidationError

from odoo.addons.mail.tests.common import MailCommon


class TestQuotationNotifications(MailCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product = cls.env["product.product"].create({"name": "Test Product"})

        cls.salesperson_1 = cls.env["res.users"].create(
            {
                "name": "Salesperson One",
                "login": "salesperson1",
                "email": "salesperson1@example.com",
            }
        )
        cls.salesperson_2 = cls.env["res.users"].create(
            {
                "name": "Salesperson Two",
                "login": "salesperson2",
                "email": "salesperson2@example.com",
            }
        )
        cls.sales_team = cls.env["crm.team"].create(
            {
                "name": "Test Sales Team",
                "member_ids": [
                    Command.set([cls.salesperson_1.id, cls.salesperson_2.id])
                ],
            }
        )

        cls.client_partner = cls.env["res.partner"].create(
            {
                "name": "Test Client",
                "email": "client@example.com",
            }
        )

        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.client_partner.id,
                "user_id": cls.salesperson_1.id,
                "team_id": cls.sales_team.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 100,
                        }
                    )
                ],
                "state": "sent",
                "typology": "quote",
            }
        )

    def test_send_confirmation_notification(self):
        """Test if the email notification is sent to the correct recipients."""

        with self.mock_mail_gateway():
            self.so.action_confirm()

            expected_recipients = self.salesperson_1 | self.salesperson_2

            self.assertMailMail(
                recipients=expected_recipients.partner_id,
                status="sent",
                mail_message=self.so.message_ids,
                email_values={
                    "subject": f"{self.so.user_id.company_id.name} "
                    f"Quotation Accepted (Ref {self.so.name})",
                    "email_from": self.so.user_id.company_id.email_formatted,
                },
            )

    def test_send_confirmation_notification_no_recipients(self):
        """Test if UserError is raised when no recipients are found."""
        sale_order_no_recipients = self.env["sale.order"].create(
            {
                "partner_id": self.client_partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 100,
                        }
                    )
                ],
                "state": "sent",
                "typology": "quote",
            }
        )
        sale_order_no_recipients.user_id = False
        sale_order_no_recipients.team_id = False

        self.assertFalse(sale_order_no_recipients.user_id)
        self.assertFalse(sale_order_no_recipients.team_id)

        with self.mock_mail_gateway():
            with self.assertRaises(
                ValidationError,
                msg="Should raise ValidationError if no recipients are found.",
            ):
                sale_order_no_recipients.action_confirm()
