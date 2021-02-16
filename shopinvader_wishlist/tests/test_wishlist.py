# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock
from odoo.addons.shopinvader.tests.common import CommonCase
from werkzeug.exceptions import NotFound


class CommonWishlistCase(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(CommonWishlistCase, cls).setUpClass()
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.prod1 = cls.env.ref("product.product_product_11")
        cls.prod2 = cls.env.ref("product.product_product_13")
        cls.prod3 = cls.env.ref("product.product_product_10")
        cls.prod4 = cls.env.ref("product.product_product_9")
        cls.prod5 = cls.env.ref("product.product_product_20")
        cls.wl_params = {
            "name": "My new wishlist :)",
            "ref": "MY_NEW",
            "partner_id": cls.partner.id,
            "lines": [
                {"product_id": cls.prod1.id, "quantity": 1.0},
                {"product_id": cls.prod2.id, "quantity": 5.0},
            ],
        }

    def setUp(self, *args, **kwargs):
        super(CommonWishlistCase, self).setUp(*args, **kwargs)
        with self.work_on_services(partner=self.partner) as work:
            self.wishlist_service = work.component(usage="wishlist")

    def _check_data(self, record, data):
        data_lines = data.pop("lines", [])
        rec_data = record._convert_to_write(record._cache)
        rec_lines = record.set_line_ids
        for key in data:
            self.assertEqual(rec_data[key], data[key])
        for dline in data_lines:
            list_line = rec_lines.filtered(
                lambda x: x.product_id.id == dline["product_id"]
            )
            self.assertTrue(list_line)
            for key in ("quantity", "sequence"):
                if key in dline:
                    self.assertEqual(list_line[key], dline.get(key))


class WishlistCase(CommonWishlistCase):
    @classmethod
    def setUpClass(cls):
        super(WishlistCase, cls).setUpClass()
        cls.prod_set = cls.env.ref("shopinvader_wishlist.wishlist_1")
        cls.prod_set.shopinvader_backend_id = cls.backend

    def test_create(self):
        params = dict(self.wl_params)
        res = self.wishlist_service.dispatch("create", params=params)["data"]
        record = self.env["product.set"].browse(res["id"])
        self.assertEqual(record.partner_id, self.partner)
        self._check_data(record, params)

    def test_update(self):
        params = {"name": "Baz"}
        self.assertEqual(self.prod_set.name, "Wishlist 1")
        self.wishlist_service.dispatch(
            "update", self.prod_set.id, params=params
        )
        self.assertEqual(self.prod_set.name, "Baz")

    def test_move_items(self):
        for line in self.wl_params["lines"]:
            self.prod_set.set_line_ids.create(
                dict(line, product_set_id=self.prod_set.id)
            )
        prod1 = self.prod_set.set_line_ids[0].product_id
        prod2 = self.prod_set.set_line_ids[1].product_id
        prod3 = self.prod_set.set_line_ids[2].product_id
        move_to_set1 = self.prod_set.copy(default={"set_line_ids": False})
        move_to_set2 = self.prod_set.copy(default={"set_line_ids": False})
        self.assertFalse(move_to_set1.set_line_ids)
        self.assertFalse(move_to_set2.set_line_ids)
        self.wishlist_service.dispatch(
            "move_items",
            self.prod_set.id,
            params={
                "lines": [
                    {
                        "move_to_wishlist_id": move_to_set1.id,
                        "product_id": prod1.id,
                    },
                    {
                        "move_to_wishlist_id": move_to_set1.id,
                        "product_id": prod2.id,
                    },
                    {
                        "move_to_wishlist_id": move_to_set2.id,
                        "product_id": prod3.id,
                    },
                ]
            },
        )
        self.assertFalse(self.prod_set.set_line_ids)
        self.assertEqual(len(move_to_set1.set_line_ids), 2)
        self.assertEqual(len(move_to_set2.set_line_ids), 1)
        self.assertIn(prod1, move_to_set1.mapped("set_line_ids.product_id"))
        self.assertIn(prod2, move_to_set1.mapped("set_line_ids.product_id"))
        self.assertIn(prod3, move_to_set2.mapped("set_line_ids.product_id"))

    def test_replace_items(self):
        for line in self.wl_params["lines"]:
            self.prod_set.set_line_ids.create(
                dict(line, product_set_id=self.prod_set.id)
            )
        prod1 = self.prod_set.set_line_ids[0].product_id
        prod2 = self.prod_set.set_line_ids[1].product_id
        prod3 = self.prod_set.set_line_ids[2].product_id
        self.wishlist_service.dispatch(
            "replace_items",
            self.prod_set.id,
            params={
                "lines": [
                    {
                        "product_id": prod1.id,
                        "replacement_product_id": self.prod3.id,
                    },
                    {
                        "product_id": prod2.id,
                        "replacement_product_id": self.prod4.id,
                    },
                    {
                        "product_id": prod3.id,
                        "replacement_product_id": self.prod5.id,
                    },
                ]
            },
        )
        set_products = self.prod_set.mapped("set_line_ids.product_id")
        self.assertNotIn(prod1, set_products)
        self.assertNotIn(prod2, set_products)
        self.assertNotIn(prod3, set_products)
        self.assertIn(self.prod3, set_products)
        self.assertIn(self.prod4, set_products)
        self.assertIn(self.prod5, set_products)

    def test_search(self):
        res = self.wishlist_service.dispatch(
            "search", params={"scope": {"typology": "foo"}}
        )
        self.assertEqual(res["size"], 0)
        res = self.wishlist_service.dispatch(
            "search", params={"scope": {"ref": "WISH_1"}}
        )
        self.assertEqual(res["size"], 1)
        self.assertEqual(res["data"][0]["ref"], "WISH_1")

    def test_get(self):
        res = self.wishlist_service.dispatch("get", self.prod_set.id)
        self.assertEqual(res["ref"], "WISH_1")

    def test_delete(self):
        self.wishlist_service.delete(self.prod_set.id)
        self.assertFalse(self.prod_set.exists())

    def test_add_to_cart(self):
        prod = self.env.ref("product.product_product_4b")
        # make sure no binding exists
        prod.shopinvader_bind_ids.unlink()

        with self.work_on_services(partner=self.partner) as work:
            cart_service = work.component(usage="cart")
        cart = cart_service._get()
        # no line yet
        self.assertFalse(cart.order_line)

        # make sure the wishlist service use the same cart
        with mock.patch.object(type(cart_service), "_get") as mocked:
            mocked.return_value = cart
            self.wishlist_service.add_to_cart(self.prod_set.id)
            # no binding for the product -> no line added
            self.assertFalse(cart.order_line)
            # bind the product and try again
            self._bind_products(prod)
            self.wishlist_service.add_to_cart(self.prod_set.id)
            self.assertEqual(cart.order_line[0].product_id, prod)

    def test_add_items_to_cart(self):
        for line in self.wl_params["lines"]:
            self.prod_set.set_line_ids.create(
                dict(line, product_set_id=self.prod_set.id)
            )
        self.assertEqual(len(self.prod_set.set_line_ids), 3)
        with self.work_on_services(partner=self.partner) as work:
            cart_service = work.component(usage="cart")
        cart = cart_service._get()
        # no line yet
        self.assertFalse(cart.order_line)

        # add only to products to cart
        prods = self.prod_set.set_line_ids[:2].mapped("product_id")
        params = {"lines": [{"product_id": x.id} for x in prods]}
        with mock.patch.object(type(cart_service), "_get") as mocked:
            mocked.return_value = cart
            self.wishlist_service.add_items_to_cart(self.prod_set.id, **params)
            self.assertEqual(cart.mapped("order_line.product_id"), prods)

    def test_add_items(self):
        prod1 = self.env.ref("product.product_product_4d")
        prod2 = self.env.ref("product.product_product_11")
        self.assertNotIn(
            prod1, self.prod_set.mapped("set_line_ids.product_id")
        )
        self.assertNotIn(
            prod2, self.prod_set.mapped("set_line_ids.product_id")
        )
        self._bind_products(prod1 + prod2)
        params = {
            "lines": [{"product_id": prod1.id}, {"product_id": prod2.id}]
        }
        self.wishlist_service.dispatch(
            "add_items", self.prod_set.id, params=params
        )
        self.assertIn(prod1, self.prod_set.mapped("set_line_ids.product_id"))
        self.assertIn(prod2, self.prod_set.mapped("set_line_ids.product_id"))

    def _test_update_items(self, prods, lines_data):
        self._bind_products(prods)
        params = {"lines": lines_data}
        self.wishlist_service.dispatch(
            "update_items", self.prod_set.id, params=params
        )
        for line in lines_data:
            line = self.prod_set.get_lines_by_products(
                product_ids=[line["product_id"]]
            )
            self.assertEqual(line.quantity, line["quantity"])

    def test_update_items(self):
        with self.assertRaises(NotFound):
            self.wishlist_service.dispatch(
                "update_items",
                self.prod_set.id,
                params={"lines": [{"product_id": 9999}]},
            )
        for line in self.wl_params["lines"]:
            self.prod_set.set_line_ids.create(
                dict(line, product_set_id=self.prod_set.id)
            )
        prod1 = self.env.ref("product.product_product_4b")
        prod2 = self.env.ref("product.product_product_11")
        prod3 = self.env.ref("product.product_product_13")
        lines = [
            {"product_id": prod1.id, "quantity": 10},
            {"product_id": prod2.id, "quantity": 15},
            {"product_id": prod3.id, "quantity": 20},
        ]
        self._test_update_items(prod1 + prod2 + prod3, lines)

    def test_update_item_order(self):
        prod1 = self.env.ref("product.product_product_4b")
        self._test_update_items(
            prod1, [{"product_id": prod1.id, "quantity": 1}]
        )
        line1 = self.prod_set.get_lines_by_products(product_ids=prod1.ids)
        line1.sequence = 10
        # Add another line and change order
        prod2 = self.env.ref("product.product_product_4d")
        self.assertNotIn(
            prod2, self.prod_set.mapped("set_line_ids.product_id")
        )
        self._bind_products(prod2)
        params = {"lines": [{"product_id": prod2.id}]}
        before = self.wishlist_service.dispatch(
            "add_items", self.prod_set.id, params=params
        )
        line2 = self.prod_set.get_lines_by_products(product_ids=prod2.ids)
        self.assertEqual(line1.sequence, 10)
        self.assertEqual(line2.sequence, 0)
        self.assertEqual(
            [x["id"] for x in before["lines"]], [line2.id, line1.id]
        )
        params = {"lines": [{"product_id": prod2.id, "sequence": 20}]}
        after = self.wishlist_service.dispatch(
            "update_items", self.prod_set.id, params=params
        )
        self.prod_set.invalidate_cache()
        self.assertEqual(line1.sequence, 10)
        self.assertEqual(line2.sequence, 20)
        self.assertEqual(
            [x["id"] for x in after["lines"]], [line1.id, line2.id]
        )

    def test_delete_items(self):
        prod = self.env.ref("product.product_product_4b")
        self._bind_products(prod)
        self.assertIn(prod, self.prod_set.mapped("set_line_ids.product_id"))
        line = self.prod_set.get_lines_by_products(product_ids=prod.ids)
        self.assertEqual(line.quantity, 1)
        params = {"lines": [{"product_id": prod.id}]}
        self.wishlist_service.dispatch(
            "delete_items", self.prod_set.id, params=params
        )
        self.assertFalse(line.exists())

    def test_jsonify(self):
        res = self.wishlist_service._to_json_one(self.prod_set)
        self.assertEqual(res["ref"], "WISH_1")
        self.assertEqual(res["name"], "Wishlist 1")
        self.assertEqual(res["typology"], "wishlist")
        self.assertEqual(
            res["partner"], {"id": self.partner.id, "name": self.partner.name}
        )
        prod = self.env.ref("product.product_product_4b")
        variant = prod.shopinvader_bind_ids[0]
        res_line = res["lines"][0]
        self.assertEqual(res_line["id"], self.prod_set.set_line_ids[0].id)
        self.assertEqual(res_line["quantity"], 1)
        self.assertEqual(res_line["sequence"], 10)
        self.assertEqual(res_line["product"], variant.get_shop_data())
