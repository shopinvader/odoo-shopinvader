# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from odoo import api, fields

from odoo.addons.shopinvader.tests.test_notification import CommonCase


class TestSaleOrder(CommonCase):
    """
    Tests for sale.order
    """

    def setUp(self):
        super().setUp()
        self.sale_obj = self.env["sale.order"]
        self.sale = self.env.ref("shopinvader.sale_order_2")
        self.template = self.env.ref(
            "shopinvader_pending_cart_reminder."
            "mail_template_shopinvader_sale_reminder"
        )
        self.backend.write(
            {
                "pending_cart_reminder_delay": 1,
                "pending_cart_reminder_template_id": self.template.id,
            }
        )
        self.days_to_add = 0

    def _patch_get_pending_cart_last_write_dt(self):
        """

        :return: function
        """
        days_to_add = self.days_to_add

        @api.model
        def _get_pending_cart_last_write_dt(self, backend):
            reminder_date = fields.Datetime.from_string(fields.Datetime.now())
            if days_to_add:
                reminder_date -= timedelta(days=days_to_add)
            return reminder_date

        return _get_pending_cart_last_write_dt

    def _patch_sale_reminder(self):
        """
        Do the patch (and add the cleanup)
        :return: bool
        """
        _get_reminder_date = self._patch_get_pending_cart_last_write_dt()
        self.sale_obj._patch_method(
            "_get_pending_cart_last_write_dt", _get_reminder_date
        )
        self.addCleanup(self.sale_obj._revert_method, "_get_pending_cart_last_write_dt")
        return True

    def _check_reminder_empty(self):
        """
        Ensure the pending_cart_reminder_sent_dt is not set
        :return: bool
        """
        self.assertFalse(self.sale.pending_cart_reminder_sent_dt)
        return True

    def _launch_and_check_no_changes(self):
        """
        Ensure no changes after launching the reminder
        :return: bool
        """
        values_before = self.sale.read()[0]
        self._patch_sale_reminder()
        self.sale_obj.launch_pending_cart_reminder()
        values_after = self.sale.read()[0]
        self.assertDictEqual(values_after, values_before)
        return True

    def test_reminder1(self):
        """
        Test the reminder
        For this case, the sale should have a reminder
        :return:
        """
        self._check_reminder_empty()
        now = fields.Datetime.from_string(fields.Datetime.now())
        self._patch_sale_reminder()
        self.sale_obj.launch_pending_cart_reminder()
        self.assertGreaterEqual(
            fields.Datetime.from_string(self.sale.pending_cart_reminder_sent_dt),
            now,
        )
        return

    def test_reminder2(self):
        """
        Test the reminder
        For this case, the sale shouldn't have a reminder
        :return:
        """
        self._check_reminder_empty()
        self.days_to_add = 4
        self._patch_sale_reminder()
        self.sale_obj.launch_pending_cart_reminder()
        self._check_reminder_empty()
        return

    def test_reminder3(self):
        """
        Test the reminder
        For this case, the sale already have a reminder and shouldn't be
        updated
        :return:
        """
        now = fields.Datetime.now()
        self.sale.write({"pending_cart_reminder_sent_dt": now})
        self._patch_sale_reminder()
        self.sale_obj.launch_pending_cart_reminder()
        self.assertEqual(self.sale.pending_cart_reminder_sent_dt, now)
        return

    def test_reminder4(self):
        """
        Test the reminder
        For this case, the sale is not a cart (but a "normal" sale)
        :return:
        """
        self.sale.write({"typology": "sale"})
        self._launch_and_check_no_changes()
        return

    def test_reminder5(self):
        """
        Test the reminder
        For this case, the partner of the sale is the anonymous user
        (so no email)
        :return:
        """
        self.sale.write({"partner_id": self.backend.anonymous_partner_id.id})
        self._launch_and_check_no_changes()
        return
