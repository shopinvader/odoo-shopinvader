# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase


class TestCart(CommonCase):
    def setUp(self):
        super(TestCart, self).setUp()
        self.cart = self.env.ref("shopinvader.sale_order_2")
        self.shopinvader_session = {"cart_id": self.cart.id}
        self.partner = self.env.ref("shopinvader.partner_1")
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="cart")

    def test_cart(self):
        online_information_for_customer = "CUSTOMER INFO"
        online_information_request = "VENDOR INFO REQUEST"
        params = {
            "online_information_for_customer": online_information_for_customer,
            "online_information_request": online_information_request,
        }
        self.service.dispatch("update", params=params)
        # online_information_for_customer should not be updated from the front
        self.assertFalse(self.cart.online_information_for_customer)
        self.assertEqual(
            self.cart.online_information_request, online_information_request
        )
