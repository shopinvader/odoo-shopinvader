# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time

from odoo.tools import float_round

from .common import CommonCase


class AbstractItemCase(object):
    def setUp(self, *args, **kwargs):
        super(AbstractItemCase, self).setUp(*args, **kwargs)
        self.product_1 = self.env.ref("product.product_product_4b")
        self.product_2 = self.env.ref("product.product_product_13")
        self.product_3 = self.env.ref("product.product_product_11")
        self.pricelist = self.env.ref("product.list0")
        self.shopinvader_backend = self.env.ref("shopinvader.backend_1")

    def extract_cart(self, response):
        self.shopinvader_session["cart_id"] = response["set_session"][
            "cart_id"
        ]
        self.assertEqual(response["store_cache"], {"cart": response["data"]})
        return response["data"]

    def add_item(self, product_id, qty):
        return self.extract_cart(
            self.service.dispatch(
                "add_item", params={"product_id": product_id, "item_qty": qty}
            )
        )

    def update_item(self, item_id, qty):
        return self.extract_cart(
            self.service.dispatch(
                "update_item", params={"item_id": item_id, "item_qty": qty}
            )
        )

    def delete_item(self, item_id):
        return self.extract_cart(
            self.service.dispatch("delete_item", params={"item_id": item_id})
        )

    def check_product_and_qty(self, line, product_id, qty):
        self.assertEqual(line["product"]["id"], product_id)
        self.assertEqual(line["qty"], qty)

    def test_add_item_without_cart(self):
        self.remove_cart()
        last_order = self.env["sale.order"].search(
            [], limit=1, order="id desc"
        )
        self.add_item(self.product_1.id, 2)
        cart = self.service.search()["data"]
        self.assertGreater(cart["id"], last_order.id)
        self.assertEqual(len(cart["lines"]["items"]), 1)
        self.assertEqual(cart["lines"]["count"], 2)
        self.check_product_and_qty(
            cart["lines"]["items"][0], self.product_1.id, 2
        )
        self.check_partner(cart)

    def test_add_item_with_an_existing_cart(self):
        cart = self.service.search()["data"]
        nbr_line = len(cart["lines"]["items"])

        cart = self.add_item(self.product_1.id, 2)
        self.assertEqual(cart["id"], self.cart.id)
        self.assertEqual(len(cart["lines"]["items"]), nbr_line + 1)
        self.check_product_and_qty(
            cart["lines"]["items"][-1], self.product_1.id, 2
        )
        self.check_partner(cart)

    def test_add_item_with_an_existing_cart_simple(self):
        self.backend.simple_cart_service = True
        cart = self.service.search()["data"]
        sale = self.env["sale.order"].browse(cart["id"])
        qty_before = sum(
            float_round(
                line.product_uom_qty,
                precision_rounding=line.product_uom.rounding,
            )
            for line in sale.order_line
        )
        nbr_line = len(cart["lines"]["items"])
        self._init_job_counter()
        cart_simple = self.add_item(self.product_1.id, 2)
        self._check_nbr_job_created(1)
        job = self.created_jobs
        self.assertEquals(
            "sale.order._shopinvader_delayed_recompute.%s" % cart.get("id"),
            job.identity_key,
        )
        self.assertEquals(
            {"id": cart["id"], "lines": {"count": qty_before + 2.0}},
            cart_simple,
        )
        cart = self.service.search()["data"]
        self.assertEqual(cart["id"], self.cart.id)
        self.assertEqual(len(cart["lines"]["items"]), nbr_line + 1)
        self.check_product_and_qty(
            cart["lines"]["items"][-1], self.product_1.id, 2
        )
        self.check_partner(cart)
        self._init_job_counter()
        self.add_item(self.product_1.id, 2)
        self._check_nbr_job_created(0)
        self._perform_created_job()

    def test_add_unbound_item_with_an_existing_cart(self):
        self.sale_line_obj = self.env["sale.order.line"]
        self.unbound_product = self.product_3.copy()
        cart = self.service.search()["data"]
        nbr_line = len(cart["lines"]["items"])
        vals = {"product_id": self.unbound_product.id}
        values = self.sale_line_obj.play_onchanges(vals)
        values.update(
            {
                "order_id": cart.get("id"),
                "product_uom_qty": 3.0,
                "product_id": self.unbound_product.id,
            }
        )
        self.line = self.sale_line_obj.create(values)
        cart = self.service.search()["data"]
        product_json = cart["lines"]["items"][-1]["product"]
        self.assertEquals(len(cart["lines"]["items"]), nbr_line + 1)
        self.assertEquals(product_json, {})
        self.shopinvader_backend.authorize_not_bound_products = True
        cart = self.service.search()["data"]
        product_json = cart["lines"]["items"][-1]["product"]
        self.assertEquals(
            product_json,
            {
                "id": self.unbound_product.id,
                "name": u"iPod",
                "sku": u"E-COM12",
            },
        )

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
        self.add_item(self.product_1.id, 1)
        cart = self.service.search()["data"]
        self.assertEqual(len(cart["lines"]["items"]), 1)
        self.check_product_and_qty(
            cart["lines"]["items"][0], self.product_1.id, 1
        )
        self.add_item(self.product_1.id, 1)
        cart = self.service.search()["data"]
        self.assertEqual(len(cart["lines"]["items"]), 1)
        self.check_product_and_qty(
            cart["lines"]["items"][0], self.product_1.id, 2
        )

    def remove_cart(self):
        self.cart.unlink()
        self.shopinvader_session.pop("cart_id")

    def _test_pricelist_product(self):
        self.remove_cart()
        # be sure that discount group is active for user
        self.env.user.write(
            {
                "groups_id": [
                    (4, self.ref("sale.group_discount_per_so_line"), 0)
                ]
            }
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
        self.add_item(self.product_3.id, 1)
        cart_data = self.service.search()["data"]
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

    def test_upgrade_last_update_date(self):
        last_external_update_date = self._get_last_external_update_date(
            self.cart
        )
        self.add_item(self.product_1.id, 2)
        self._check_last_external_update_date(
            self.cart, last_external_update_date
        )

        time.sleep(1)

        last_external_update_date = self._get_last_external_update_date(
            self.cart
        )
        line_id = self.cart.order_line[0].id
        self.update_item(line_id, 5)
        self._check_last_external_update_date(
            self.cart, last_external_update_date
        )

        time.sleep(1)

        last_external_update_date = self._get_last_external_update_date(
            self.cart
        )
        self.delete_item(line_id)
        self._check_last_external_update_date(
            self.cart, last_external_update_date
        )


class AnonymousItemCase(AbstractItemCase, CommonCase):
    def setUp(self, *args, **kwargs):
        super(AnonymousItemCase, self).setUp(*args, **kwargs)
        self.partner = self.backend.anonymous_partner_id
        self.cart = self.env.ref("shopinvader.sale_order_1")
        self.cart.order_line._compute_shopinvader_variant()
        self.shopinvader_session = {"cart_id": self.cart.id}
        with self.work_on_services(
            partner=None, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="cart")

    def check_partner(self, cart):
        self.assertEqual(cart["shipping"]["address"], {})
        self.assertEqual(cart["invoicing"]["address"], {})


class ConnectedItemCase(AbstractItemCase, CommonCase):
    def setUp(self, *args, **kwargs):
        super(ConnectedItemCase, self).setUp(*args, **kwargs)
        self.partner = self.env.ref("shopinvader.partner_1")
        self.cart = self.env.ref("shopinvader.sale_order_2")
        self.cart.order_line._compute_shopinvader_variant()
        self.shopinvader_session = {"cart_id": self.cart.id}
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="cart")

    def check_partner(self, cart):
        self.assertEqual(cart["shipping"]["address"]["id"], self.partner.id)
        self.assertEqual(cart["invoicing"]["address"]["id"], self.partner.id)
