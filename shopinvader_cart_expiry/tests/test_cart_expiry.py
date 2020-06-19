# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

import mock
from odoo import fields
from odoo.addons.shopinvader.tests.test_cart import CartCase


class TestCartExpiry(CartCase):
    """
    Tests for cart expiry
    """

    def setUp(self):
        super(TestCartExpiry, self).setUp()
        self.sale_obj = self.env["sale.order"]
        self.partner = self.env.ref("shopinvader.partner_1")
        self.sale = self.env.ref("shopinvader.sale_order_2")
        self.cart = self.env.ref("shopinvader.sale_order_2")
        self.shopinvader_session = {"cart_id": self.cart.id}
        with self.work_on_services(
            partner=None, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="cart")

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

    def test_cart_expiration_date(self):
        so_date = fields.Datetime.from_string(self.sale.write_date)
        today = fields.Datetime.to_string(so_date + timedelta(hours=5))
        self.backend.write(
            {"cart_expiry_delay": 1, "cart_expiry_policy": "cancel"}
        )
        now_method = "odoo.fields.Datetime.now"
        with mock.patch(now_method) as mock_now:
            mock_now.return_value = today
            expiration_date = so_date + timedelta(days=1)
            self.assertEquals(expiration_date, self.sale.cart_expiration_date)
            cart = self.service.search()
            self.assertDictContainsSubset(
                {"expiration_date": expiration_date}, cart.get("data")
            )

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

    def test_new_cart_expiration_date(self):
        today = fields.Datetime.now()
        self.backend.write(
            {"cart_expiry_delay": 1, "cart_expiry_policy": "cancel"}
        )
        # Void Session
        self.shopinvader_session = {}
        with self.work_on_services(
            partner=None, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="cart")

        # Add item
        now_method = "odoo.fields.Datetime.now"
        with mock.patch(now_method) as mock_now:
            mock_now.return_value = today
            response = self.service.dispatch(
                "add_item",
                params={
                    "product_id": self.env.ref("product.product_product_3").id,
                    "item_qty": 2.0,
                },
            )
            self.shopinvader_session["cart_id"] = response["set_session"][
                "cart_id"
            ]
            sale = self.env["sale.order"].browse(
                self.shopinvader_session.get("cart_id")
            )
            cart = self.service.search()
            self.assertDictContainsSubset(
                {"expiration_date": sale.cart_expiration_date},
                cart.get("data"),
            )

    def test_cart_expiry_not_draft(self):
        """
        Ensure the cart is not deleted/canceled when the state is not draft.
        :return:
        """
        so_date = fields.Datetime.from_string(self.sale.write_date)
        today = fields.Datetime.to_string(so_date + timedelta(hours=5))
        self.sale.write({"state": "sent"})
        self.backend.write(
            {"cart_expiry_delay": 1, "cart_expiry_policy": "cancel"}
        )
        now_method = "odoo.fields.Datetime.now"
        with mock.patch(now_method) as mock_now:
            mock_now.return_value = today
            self.backend.manage_cart_expiry()
            # The state still "sent"
            self.assertEqual(self.sale.state, "sent")

        today = fields.Datetime.to_string(so_date + timedelta(days=2))
        with mock.patch(now_method) as mock_now:
            mock_now.return_value = today
            self.backend.manage_cart_expiry()
            self.assertTrue(self.sale.exists())
            self.assertEqual(self.sale.state, "sent")
            # Then re-update the cart to draft state
            self.sale.write({"state": "draft"})
            self.backend.manage_cart_expiry()
            self.assertEqual(self.sale.state, "cancel")
