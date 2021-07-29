# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields

from odoo.addons.shopinvader.tests.common import CommonCase


class TestShopinvaderBackend(CommonCase):
    """
    Tests for shopinvader.backend
    """

    def setUp(self):
        super().setUp()
        self.template = self.env.ref(
            "shopinvader_pending_cart_reminder."
            "mail_template_shopinvader_sale_reminder"
        )
        self.backend.write({"pending_cart_reminder_template_id": self.template.id})

    def test_auto_reminder_start_date(self):
        """
        Ensure the reminder_start_date is correctly updated
        :return:
        """
        # Set to a previous date and disable the reminder
        today = "2019-01-01"
        reminder = 0
        self.backend.write(
            {
                "pending_cart_reminder_delay": reminder,
                "reminder_start_date": today,
            }
        )
        # Ensure the write is done
        self.assertEqual(self.backend.pending_cart_reminder_delay, reminder)
        self.assertEqual(
            self.backend.reminder_start_date, fields.Date.from_string(today)
        )
        # Now enable the reminder
        today = fields.Date.today()
        reminder = 10
        self.backend.write({"pending_cart_reminder_delay": reminder})
        # Ensure the reminder_start_date is updated
        self.assertEqual(self.backend.pending_cart_reminder_delay, reminder)
        self.assertEqual(self.backend.reminder_start_date, today)
        # Disable the reminder
        reminder = 0
        self.backend.write({"pending_cart_reminder_delay": reminder})
        # The date shouldn't change
        self.assertEqual(self.backend.pending_cart_reminder_delay, reminder)
        self.assertEqual(self.backend.reminder_start_date, today)
        return
