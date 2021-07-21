# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tools import mute_logger

from .common import CommonCase


class ItemCaseMixin(object):
    @classmethod
    def _setup_products(cls):
        cls.product_1 = cls.env.ref("product.product_product_4b")
        cls.product_2 = cls.env.ref("product.product_product_13")
        cls.product_3 = cls.env.ref("product.product_product_11")
        cls.pricelist = cls.env.ref("product.list0")

    def extract_cart(self, response):
        self.shopinvader_session["cart_id"] = response["set_session"]["cart_id"]
        self.assertEqual(response["store_cache"], {"cart": response["data"]})
        return response["data"]

    def add_item(self, product_id, qty, **kw):
        params = {"product_id": product_id, "item_qty": qty}
        params.update(kw)
        return self.extract_cart(self.service.dispatch("add_item", params=params))

    def update_item(self, item_id, qty, **kw):
        params = {"item_id": item_id, "item_qty": qty}
        params.update(kw)
        return self.extract_cart(self.service.dispatch("update_item", params=params))

    def delete_item(self, item_id):
        return self.extract_cart(
            self.service.dispatch("delete_item", params={"item_id": item_id})
        )

    def check_product_and_qty(self, line, product_id, qty):
        self.assertEqual(line["product"]["id"], product_id)
        self.assertEqual(line["qty"], qty)

    @mute_logger("odoo.models.unlink")
    def remove_cart(self):
        self.cart.unlink()
        self.shopinvader_session.pop("cart_id")


class AbstractItemCase(ItemCaseMixin):
    @classmethod
    def setUpClass(cls):
        super(AbstractItemCase, cls).setUpClass()
        cls._setup_products()

    def test_add_item_without_cart(self):
        self.remove_cart()
        last_order = self.env["sale.order"].search([], limit=1, order="id desc")
        cart = self.add_item(self.product_1.id, 2)
        self.assertGreater(cart["id"], last_order.id)
        self.assertEqual(len(cart["lines"]["items"]), 1)
        self.assertEqual(cart["lines"]["count"], 2)
        self.check_product_and_qty(cart["lines"]["items"][0], self.product_1.id, 2)
        self.check_partner(cart)

    def test_add_item_with_an_existing_cart(self):
        cart = self.service.search()["data"]
        nbr_line = len(cart["lines"]["items"])

        cart = self.add_item(self.product_1.id, 2)
        self.assertEqual(cart["id"], self.cart.id)
        self.assertEqual(len(cart["lines"]["items"]), nbr_line + 1)
        self.check_product_and_qty(cart["lines"]["items"][-1], self.product_1.id, 2)
        self.check_partner(cart)

    def test_update_item(self):
        line_id = self.cart.order_line[0].id
        product_id = self.cart.order_line[0].product_id.id
        cart = self.update_item(line_id, 5)
        self.check_product_and_qty(cart["lines"]["items"][0], product_id, 5)
        self.assertEqual(self.cart.id, cart["id"])

    def test_update_item_robustness(self):
        """
        In this case we update an item on confirmed cart...
        As result, a new item will be added on a new cart with the expectd qty
        """
        # by changing the typology, the cart is no more available on
        # the cart service
        self.cart.typology = "sale"
        line_id = self.cart.order_line[0].id
        product_id = self.cart.order_line[0].product_id.id
        cart = self.update_item(line_id, 5)
        self.check_product_and_qty(cart["lines"]["items"][0], product_id, 5)
        # A new line has been created on a new cart...
        self.assertNotEqual(self.cart.id, cart["id"])

    @mute_logger("odoo.models.unlink")
    def test_delete_item(self):
        cart = self.service.search()["data"]
        cart_id = cart["id"]
        items = cart["lines"]["items"]
        nbr_line = len(items)
        cart = self.delete_item(items[0]["id"])
        self.assertEqual(len(cart["lines"]["items"]), nbr_line - 1)
        self.assertEqual(cart_id, cart["id"])

    def test_delete_item_robustness(self):
        """
        In this case we remove an item of a confirmed cart...
        The deletion must be ignored.. and a new empty cart returned
        """
        # by changing the typology, the cart is no more available on
        # the cart service
        self.cart.typology = "sale"
        line_id = self.cart.order_line[0].id
        cart = self.delete_item(line_id)
        self.assertEqual(len(cart["lines"]["items"]), 0)
        self.assertNotEqual(self.cart.id, cart["id"])

    def test_add_item_with_same_product_without_cart(self):
        self.remove_cart()
        cart = self.add_item(self.product_1.id, 1)
        self.assertEqual(len(cart["lines"]["items"]), 1)
        self.check_product_and_qty(cart["lines"]["items"][0], self.product_1.id, 1)
        cart = self.add_item(self.product_1.id, 1)
        self.assertEqual(len(cart["lines"]["items"]), 1)
        self.check_product_and_qty(cart["lines"]["items"][0], self.product_1.id, 2)

    @mute_logger("odoo.models.unlink")
    def test_add_item_with_product_not_allowed(self):
        self.remove_cart()
        # drop bindings and try to add the product
        self.product_1.shopinvader_bind_ids.unlink()
        with self.assertRaises(exceptions.UserError):
            self.add_item(self.product_1.id, 1)

    def _test_pricelist_product(self):
        self.remove_cart()
        # be sure that discount group is active for user
        self.env.user.write(
            {"groups_id": [(4, self.ref("product.group_discount_per_so_line"), 0)]}
        )
        # we create a new pricelist for the product with a discount of 10%
        self.env["product.pricelist.item"].create(
            {
                "base": "list_price",
                "percent_price": 10,
                "name": "Product discount Ipod",
                "pricelist_id": self.pricelist.id,
                "compute_price": "percentage",
                "applied_on": "0_product_variant",
                "product_id": self.product_3.id,
            }
        )
        cart_data = self.add_item(self.product_3.id, 1)
        cart = self.env["sale.order"].browse(cart_data["id"])
        self.assertEqual(cart.pricelist_id, self.pricelist)
        return cart_data["lines"]["items"][0]["amount"]

    def test_pricelist_product_price_unit_without_discount(self):
        self.pricelist.discount_policy = "without_discount"
        amount = self._test_pricelist_product()
        # into the cart, the price must be the price without discount
        self.assertEqual(amount["price"], 16.5)
        # but the total for the line into the cart info must be the price with
        # discount
        self.assertEqual(amount["total"], 14.85)

    def test_pricelist_product_price_unit_with_discount(self):
        self.pricelist.discount_policy = "with_discount"
        amount = self._test_pricelist_product()
        # into the cart, the price must be the price with discount
        self.assertEqual(amount["price"], 14.85)
        # same for the total
        self.assertEqual(amount["total"], 14.85)


class AnonymousItemCase(AbstractItemCase, CommonCase):
    @classmethod
    def setUpClass(cls):
        super(AnonymousItemCase, cls).setUpClass()
        cls.partner = cls.backend.anonymous_partner_id
        cls.cart = cls.env.ref("shopinvader.sale_order_1")

    def setUp(self, *args, **kwargs):
        super(AnonymousItemCase, self).setUp(*args, **kwargs)
        self.shopinvader_session = {"cart_id": self.cart.id}
        with self.work_on_services(
            partner=None, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="cart")

    def check_partner(self, cart):
        self.assertEqual(cart["shipping"]["address"], {})
        self.assertEqual(cart["invoicing"]["address"], {})


class ConnectedItemCase(AbstractItemCase, CommonCase):
    @classmethod
    def setUpClass(cls):
        super(ConnectedItemCase, cls).setUpClass()
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.cart = cls.env.ref("shopinvader.sale_order_2")

    def setUp(self, *args, **kwargs):
        super(ConnectedItemCase, self).setUp(*args, **kwargs)
        self.shopinvader_session = {"cart_id": self.cart.id}
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="cart")

    def check_partner(self, cart):
        self.assertEqual(cart["shipping"]["address"]["id"], self.partner.id)
        self.assertEqual(cart["invoicing"]["address"]["id"], self.partner.id)
