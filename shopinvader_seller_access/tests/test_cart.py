from odoo import fields
from odoo.exceptions import AccessDenied, MissingError
from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase

from .common import SellerGroupBackendMixin


class TestCart(SellerGroupBackendMixin, CommonConnectedCartCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_2 = cls.env.ref("shopinvader.partner_2")
        cls.user_of_partner_2 = cls.env["res.users"].create(
            {
                "login": "partner_2",
                "partner_id": cls.partner_2.id,
            }
        )

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        # We have no session here
        with self.work_on_services(partner=self.partner_2) as work:
            self.service_as_seller = work.component(usage="cart")

    def test_get_cart_as_customer(self):
        # Clear existing carts
        self.backend.clear_cart_options = "cancel"
        self.service_as_seller.dispatch("clear")

        # Create a new cart by adding an item
        cart = self.service_as_seller.dispatch(
            "add_item",
            params={
                "product_id": self.product_1.id,
                "item_qty": 1,
            },
        )["data"]
        cart_id = cart["id"]

        self.assertEquals(cart["lines"]["count"], 1)
        # This cart partner is the customer that created it
        self.assertEquals(cart["shipping"]["address"]["id"], self.partner_2.id)

        cart = self.service_as_seller.dispatch(
            "add_item",
            params={
                "product_id": 1,
                "item_qty": 1,
            },
        )["data"]

        self.assertEquals(cart["id"], cart_id)
        self.assertEquals(cart["lines"]["count"], 2)
        self.assertEquals(cart["shipping"]["address"]["id"], self.partner_2.id)

    def test_get_cart_as_seller(self):
        # Then create a cart for partner as partner_2
        with self.seller_group():
            cart = self.service_as_seller.dispatch(
                "create_for", params={"customer_id": self.partner.id}
            )["data"]
            cart_id = cart["id"]

        # This cart partner should be the one specified in customer_id parameter
        self.assertEquals(cart["shipping"]["address"]["id"], self.partner.id)

        with self.seller_group():
            cart = self.service_as_seller.dispatch(
                "add_item",
                params={
                    "product_id": self.product_1.id,
                    "item_qty": 1,
                },
            )["data"]

        # This must be the same cart
        self.assertEquals(cart["id"], cart_id)
        self.assertEquals(cart["lines"]["count"], 1)
        self.assertEquals(cart["shipping"]["address"]["id"], self.partner.id)

        with self.seller_group():
            partner_cart = self.service_as_seller.dispatch("search")["data"]
        self.assertEquals(cart, partner_cart)

        with self.seller_group():
            cart = self.service_as_seller.dispatch(
                "add_item",
                params={
                    "product_id": 1,
                    "item_qty": 1,
                },
            )["data"]

        self.assertEquals(cart["id"], cart_id)
        self.assertEquals(cart["lines"]["count"], 2)
        self.assertEquals(cart["shipping"]["address"]["id"], self.partner.id)

    def test_create_cart_for_as_non_seller(self):
        with self.assertRaises(MissingError) as e:
            with self.seller_group():
                self.service.dispatch(
                    "create_for", params={"customer_id": self.partner.id}
                )
        self.assertEquals(
            str(e.exception), "Partner osiris@shopinvader.com is not a user"
        )

    def test_create_cart_for_as_non_seller_not_in_group(self):
        with self.assertRaises(AccessDenied) as e:
            with self.seller_group("buyer"):
                self.service_as_seller.dispatch(
                    "create_for", params={"customer_id": self.partner.id}
                )
        self.assertEquals(
            str(e.exception), "seller group is required and not present in ['buyer']"
        )

    def test_create_cart_for_without_seller_access(self):
        self.backend.seller_access = False
        with self.assertRaises(AccessDenied) as e:
            with self.seller_group():
                self.service_as_seller.dispatch(
                    "create_for", params={"customer_id": self.partner.id}
                )
        self.assertEquals(
            str(e.exception), "This backend does not support seller access"
        )

    def test_get_cart_with_a_partner_without_user(self):
        cart = self.service.dispatch("search")["data"]
        self.assertEquals(cart["id"], self.cart.id)

    def test_get_cart_as_non_seller(self):
        with self.seller_group():
            cart = self.service_as_seller.dispatch(
                "create_for", params={"customer_id": self.partner.id}
            )["data"]
            cart_id = cart["id"]

            # We get the cart for partner since we are seller
            cart = self.service_as_seller.dispatch("search")["data"]
            self.assertEquals(cart["id"], cart_id)

        # We should not get the cart from partner since we are not seller
        # even if the cart has us as seller
        cart = self.service_as_seller.dispatch("search")["data"]
        self.assertNotEquals(cart["id"], cart_id)

    def test_cart_ask_email_as_seller_for_not_owned_cart(self):
        self._create_notification_config()
        now = fields.Date.today()
        with self.seller_group():
            self.service_as_seller.dispatch("ask_email", self.cart.id)

        notif = "cart_send_email"
        description = "Notify {} for {},{}".format(notif, self.cart._name, self.cart.id)
        domain = [("name", "=", description), ("date_created", ">=", now)]
        # It should not create any queue job because the partner is not the seller of the cart
        self.assertEqual(self.env["queue.job"].search_count(domain), 0)

    def test_cart_ask_email_as_seller_for_owned_cart(self):
        self._create_notification_config()
        with self.seller_group():
            cart = self.service_as_seller.dispatch(
                "create_for", params={"customer_id": self.partner.id}
            )["data"]
            cart_id = cart["id"]

        now = fields.Date.today()
        with self.seller_group():
            self.service_as_seller.dispatch("ask_email", cart_id)

        notif = "cart_send_email"
        description = "Notify {} for {},{}".format(notif, self.cart._name, cart_id)
        domain = [("name", "=", description), ("date_created", ">=", now)]
        # It creates the queue job because the partner is the seller of the cart
        self.assertEqual(self.env["queue.job"].search_count(domain), 1)

    def test_cart_ask_email_as_non_seller_for_owned_cart(self):
        self._create_notification_config()
        with self.seller_group():
            cart = self.service_as_seller.dispatch(
                "create_for", params={"customer_id": self.partner.id}
            )["data"]
            cart_id = cart["id"]

        now = fields.Date.today()
        with self.seller_group("buyer"):
            self.service_as_seller.dispatch("ask_email", cart_id)

        notif = "cart_send_email"
        description = "Notify {} for {},{}".format(notif, self.cart._name, cart_id)
        domain = [("name", "=", description), ("date_created", ">=", now)]
        # It should not create any queue job because the user is not a seller
        self.assertEqual(self.env["queue.job"].search_count(domain), 0)
