# Copyright 2021 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import MissingError

from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase


class CommonConnectedMultiCartCase(CommonConnectedCartCase):
    """ Common class for connected multi cart tests """

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        # TODO: This should be done in setUpClass, but it needs
        # to be changed in shopinvader's CommonConnectedCartCase
        # Link sale_order_1 to our partner
        self.cart_2 = self.env.ref("shopinvader.sale_order_1")
        self.cart_2.partner_id = self.partner
        self.carts = self.cart | self.cart_2
        # rename service -> cart_service
        self.cart_service = self.service
        # multiple carts service
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="carts")

    def _update_shopinvader_session_from_response(self, response):
        if "set_session" in response:
            self.shopinvader_session.update(response["set_session"])


class TestCarts(CommonConnectedMultiCartCase):
    def test_carts_search(self):
        res = self.service.dispatch("search")
        cart_ids = {cart["id"] for cart in res["data"]}
        self.assertEqual(cart_ids, set(self.carts.ids))

    def test_carts_search_unauthorized(self):
        # cart_2 now belongs to another partner
        self.cart_2.partner_id = self.env.ref("shopinvader.anonymous")
        res = self.service.dispatch("search")
        cart_ids = {cart["id"] for cart in res["data"]}
        self.assertEqual(cart_ids, set(self.cart.ids))

    def test_carts_select(self):
        self.assertEqual(self.cart_service.cart_id, self.cart.id)
        res = self.service.dispatch("select", self.cart_2.id)
        self._update_shopinvader_session_from_response(res)
        self.assertEqual(
            self.cart_service.cart_id,
            self.cart_2.id,
            "Current cart should've been changed from session",
        )

    def test_carts_select_unauthorized(self):
        # cart_2 now belongs to another partner
        self.cart_2.partner_id = self.env.ref("shopinvader.anonymous")
        with self.assertRaises(MissingError):
            self.service.dispatch("select", self.cart_2.id)

    def test_carts_delete(self):
        # Case 1: Delete secondary cart
        res = self.service.dispatch("delete", self.cart_2.id)
        self._update_shopinvader_session_from_response(res)
        self.assertEqual(len(self.carts.exists()), 1, "Only one cart should be left")
        self.assertEqual(
            self.cart_service.cart_id,
            self.cart.id,
            "Current cart should remain unchanged from session",
        )
        # Case 2: Delete the main cart
        res = self.service.dispatch("delete", self.cart.id)
        self._update_shopinvader_session_from_response(res)
        self.assertEqual(len(self.carts.exists()), 0, "All carts removed")
        self.assertEqual(
            self.cart_service.cart_id,
            0,
            "Current cart should've been cleared from session",
        )

    def test_carts_delete_unauthorized(self):
        # cart_2 now belongs to another partner
        self.cart_2.partner_id = self.env.ref("shopinvader.anonymous")
        with self.assertRaises(MissingError):
            self.service.dispatch("delete", self.cart_2.id)
