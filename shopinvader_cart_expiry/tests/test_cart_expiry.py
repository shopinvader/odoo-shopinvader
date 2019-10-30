# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

import mock
from odoo import fields
from odoo.addons.shopinvader.tests.common import CommonCase


class TestCartExpiry(CommonCase):
    """
    Tests for cart expiry
    """

    def setUp(self):
        super(TestCartExpiry, self).setUp()
        self.sale_obj = self.env["sale.order"]
        self.sale = self.env.ref("shopinvader.sale_order_2")

    def test_cart_expiry_scheduler(self):
        """
        :return:
        """
        self._init_job_counter()
        self.backend.write({"cart_expiry_delay": 0})
        self.env["shopinvader.backend"]._scheduler_manage_cart_expiry()
        self._check_nbr_job_created(0)

        self._init_job_counter()
        self.backend.write({"cart_expiry_delay": 1})
        self.env["shopinvader.backend"]._scheduler_manage_cart_expiry()
        self._check_nbr_job_created(1)
        return

    def test_cart_expiry_cancel(self):
        so_date = fields.Datetime.from_string(self.sale.write_date)
        today = fields.Datetime.to_string(so_date + timedelta(hours=5))
        self.backend.write(
            {"cart_expiry_delay": 1, "cart_expiry_policy": "cancel"}
        )
        now_method = "odoo.fields.Datetime.now"
        with mock.patch(now_method) as mock_now:
            mock_now.return_value = today
            self.backend.manage_cart_expiry()
            self.assertEqual(self.sale.state, "draft")

        today = fields.Datetime.to_string(so_date + timedelta(days=2))
        with mock.patch(now_method) as mock_now:
            mock_now.return_value = today
            self.backend.manage_cart_expiry()
            self.assertEqual(self.sale.state, "cancel")

    def test_cart_expiry_delete(self):
        so_date = fields.Datetime.from_string(self.sale.write_date)
        today = fields.Datetime.to_string(so_date + timedelta(hours=5))
        self.backend.write(
            {"cart_expiry_delay": 1, "cart_expiry_policy": "delete"}
        )
        now_method = "odoo.fields.Datetime.now"
        with mock.patch(now_method) as mock_now:
            mock_now.return_value = today
            self.backend.manage_cart_expiry()
            self.assertEqual(self.sale.state, "draft")

        today = fields.Datetime.to_string(so_date + timedelta(days=2))
        with mock.patch(now_method) as mock_now:
            mock_now.return_value = today
            self.backend.manage_cart_expiry()
            self.assertFalse(self.sale.exists())
