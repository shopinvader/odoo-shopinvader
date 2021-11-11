# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import MissingError

from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase


class CommonConnectedMultiCartCase(CommonConnectedCartCase):
    """ Common class for connected multi cart tests """

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        # TODO: This should be done in setUpClass, but it needs
        # to be changed in shopinvader's CommonConnectedCartCase
        self.saved_cart = self.cart.copy(
            {
                "typology": "saved",
            }
        )
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

    def _search(self):
        """Wrapper around `search` to return only cart_ids"""
        res = self.service.dispatch("search")
        cart_ids = list({cart["id"] for cart in res["data"]})
        return cart_ids

    def _select(self, cart_id):
        """Wrapper around `select` that updates shopinvader_session"""
        res = self.service.dispatch("select", cart_id)
        self._update_shopinvader_session_from_response(res)
        return res

    def _delete(self, cart_id):
        """Wrapper around `delete` that updates shopinvader_session"""
        res = self.service.dispatch("delete", cart_id)
        self._update_shopinvader_session_from_response(res)
        return res

    def _save(self):
        """Wrapper around cart_service's `save` that updates shopinvader_session"""
        res = self.cart_service.dispatch("save")
        self._update_shopinvader_session_from_response(res)
        return res


class TestCarts(CommonConnectedMultiCartCase):
    def test_carts_search(self):
        self.assertEqual(self._search(), self.saved_cart.ids)

    def test_carts_search_unauthorized(self):
        # saved_cart now belongs to another partner
        self.saved_cart.partner_id = self.env.ref("shopinvader.anonymous")
        self.assertFalse(self._search())

    def test_carts_select(self):
        self._select(self.saved_cart.id)
        self.assertEqual(
            self.cart_service.cart_id,
            self.saved_cart.id,
            "Current cart should've been changed from session",
        )
        self.assertEqual(
            self._search(), self.cart.ids, "The previous cart should've been saved"
        )

    def test_carts_select_unauthorized(self):
        # saved_cart now belongs to another partner
        self.saved_cart.partner_id = self.env.ref("shopinvader.anonymous")
        with self.assertRaises(MissingError):
            self._select(self.saved_cart.id)
        self.assertEqual(
            self.cart_service.cart_id,
            self.cart.id,
            "Current cart shouldn't have been changed from session",
        )

    def test_carts_delete(self):
        self._delete(self.saved_cart.id)
        self.assertFalse(self.saved_cart.exists())
        self.assertEqual(
            self.cart_service.cart_id,
            self.cart.id,
            "Current cart should remain unchanged from session",
        )

    def test_carts_delete_unauthorized(self):
        # saved_cart now belongs to another partner
        self.saved_cart.partner_id = self.env.ref("shopinvader.anonymous")
        with self.assertRaises(MissingError):
            self._delete(self.saved_cart.id)

    def test_cart_save(self):
        self._save()
        self.assertFalse(
            self.cart_service.cart_id,
            "The cart should've been cleared from session",
        )
        self.assertIn(self.cart.id, self._search(), "The cart should've been saved")

    def test_cart_save_without_cart(self):
        self.cart.unlink()
        self._save()  # nothing should happen
