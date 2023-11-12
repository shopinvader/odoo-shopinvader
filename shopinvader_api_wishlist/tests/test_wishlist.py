# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from .common import CommonWishlistCase


class WishlistCase(CommonWishlistCase):
    @classmethod
    def setUpClass(cls):
        super(WishlistCase, cls).setUpClass()
        cls.prod_set = cls.env["product.set"].create(
            {
                "name": "Wishlist 1",
                "ref": "WISH_1",
                "typology": "wishlist",
                "partner_id": cls.partner.id,
                "set_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.prod6.id,
                            "quantity": 5.0,
                            "sequence": 0,
                        },
                    ),
                ],
            }
        )

    def test_create(self):
        with self._create_test_client(partner=self.partner) as client:
            res = client.post("/wishlists", json=self.wl_params)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["ref"], "MY_NEW")
        record = self.env["product.set"].browse(res.json()["id"])
        self.assertEqual(record.partner_id, self.partner)
        self._check_data(record, dict(self.wl_params))

    def test_update(self):
        self.assertEqual(self.prod_set.name, "Wishlist 1")
        params = {"name": "Baz"}
        with self._create_test_client(partner=self.partner) as client:
            res = client.put(f"/wishlists/{self.prod_set.id}", json=params)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["name"], "Baz")
        self.assertEqual(self.prod_set.name, "Baz")

    def test_update_with_lines(self):
        for line in self.wl_params["lines"]:
            self.prod_set.set_line_ids.create(
                dict(line, product_set_id=self.prod_set.id)
            )
        # A product is already into the cart and we added new lines from wl_params
        self.assertEqual(
            len(self.prod_set.set_line_ids), len(self.wl_params["lines"]) + 1
        )

        lines = self.wl_params["lines"][:-1]
        for line in lines:
            line["quantity"] = 100
        params = {"lines": lines, "ref": "new_ref"}
        with self._create_test_client(partner=self.partner) as test_client:
            res = test_client.put(f"/wishlists/{self.prod_set.id}", json=params)

        self.assertEqual(res.status_code, 200)
        result = res.json()
        self.assertEqual(result["ref"], "new_ref")
        self.assertEqual(len(result["lines"]), len(lines))
        for line in result["lines"]:
            self.assertEqual(line["quantity"], 100)

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
        params = {
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
        }
        with self._create_test_client(partner=self.partner) as client:
            res = client.post(f"/wishlists/{self.prod_set.id}/move_items", json=params)
        self.assertEqual(res.status_code, 200)
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
        params = {
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
        }
        with self._create_test_client(partner=self.partner) as test_client:
            res = test_client.post(
                f"/wishlists/{self.prod_set.id}/replace_items", json=params
            )
        self.assertEqual(res.status_code, 200)
        set_products = self.prod_set.mapped("set_line_ids.product_id")
        self.assertNotIn(prod1, set_products)
        self.assertNotIn(prod2, set_products)
        self.assertNotIn(prod3, set_products)
        self.assertIn(self.prod3, set_products)
        self.assertIn(self.prod4, set_products)
        self.assertIn(self.prod5, set_products)

    def test_search(self):
        with self._create_test_client(partner=self.partner) as test_client:
            res = test_client.get("/wishlists")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["count"], 1)
        with self._create_test_client(partner=self.not_allowed_partner) as test_client:
            res = test_client.get("/wishlists")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["count"], 0)

        with self._create_test_client(partner=self.partner) as test_client:
            res = test_client.get("/wishlists", params={"ref": "WISH_1"})
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json()["count"], 1)
            res = test_client.get("/wishlists", params={"name": "wish"})
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json()["count"], 1)

    def test_get(self):
        with self._create_test_client(partner=self.partner) as test_client:
            res = test_client.get(f"/wishlists/{self.prod_set.id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["ref"], "WISH_1")

    def test_delete(self):
        with self._create_test_client(partner=self.partner) as test_client:
            res = test_client.delete(f"/wishlists/{self.prod_set.id}")
        self.assertEqual(res.status_code, 204)
        self.assertFalse(self.prod_set.exists())

    def test_add_to_cart(self):
        cart = self.env["sale.order"]._create_empty_cart(self.partner.id)
        self.assertFalse(cart.order_line)

        # make sure the wishlist service use the same cart
        with self._create_test_client(partner=self.partner) as test_client:
            res = test_client.post(f"/wishlists/{self.prod_set.id}/add_to_cart")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            cart.order_line[0].product_id, self.prod_set.set_line_ids.product_id
        )

    def test_add_items_to_cart(self):
        for line in self.wl_params["lines"]:
            self.prod_set.set_line_ids.create(
                dict(line, product_set_id=self.prod_set.id)
            )
        self.assertEqual(len(self.prod_set.set_line_ids), 3)
        cart = self.env["sale.order"]._create_empty_cart(self.partner.id)
        # no line yet
        self.assertFalse(cart.order_line)

        # add only two products to cart
        prods = self.prod_set.set_line_ids[:2].mapped("product_id")
        params = {"lines": [{"product_id": x.id} for x in prods]}
        with self._create_test_client(partner=self.partner) as test_client:
            res = test_client.post(
                f"/wishlists/{self.prod_set.id}/add_items_to_cart", json=params
            )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(cart.mapped("order_line.product_id"), prods)

    def test_add_items(self):
        self.assertNotIn(self.prod1, self.prod_set.mapped("set_line_ids.product_id"))
        self.assertNotIn(self.prod2, self.prod_set.mapped("set_line_ids.product_id"))
        params = {
            "lines": [{"product_id": self.prod1.id}, {"product_id": self.prod2.id}]
        }
        with self._create_test_client(partner=self.partner) as test_client:
            res = test_client.post(
                f"/wishlists/{self.prod_set.id}/add_items", json=params
            )
        self.assertEqual(res.status_code, 200)
        self.assertIn(self.prod1, self.prod_set.mapped("set_line_ids.product_id"))
        self.assertIn(self.prod2, self.prod_set.mapped("set_line_ids.product_id"))

    def _test_update_items(self, prods, lines_data):
        params = {"lines": lines_data}
        with self._create_test_client(partner=self.partner) as test_client:
            res = test_client.post(
                f"/wishlists/{self.prod_set.id}/update_items", json=params
            )
        self.assertEqual(res.status_code, 200)
        for line in lines_data:
            set_line = self.prod_set.set_line_ids.filtered(
                lambda x, l=line: x.product_id.id == l["product_id"]
            )
            self.assertEqual(len(set_line), 1)
            self.assertEqual(set_line.quantity, line["quantity"])
        return res

    def test_update_items(self):
        for line in self.wl_params["lines"]:
            self.prod_set.set_line_ids.create(
                dict(line, product_set_id=self.prod_set.id)
            )
        initial_count_lines = len(self.prod_set.set_line_ids)
        lines = [
            {"product_id": self.prod1.id, "quantity": 10},
            {"product_id": self.prod2.id, "quantity": 15},
        ]
        res = self._test_update_items(self.prod1 + self.prod2, lines)
        self.assertEqual(len(res.json()["lines"]), initial_count_lines)
        # a new call should do nothing
        res = self._test_update_items(self.prod1 + self.prod2, lines)
        self.assertEqual(len(res.json()["lines"]), initial_count_lines)

    def test_update_item_order(self):
        self.prod_set.set_line_ids.unlink()
        params = {"lines": [{"product_id": self.prod1.id, "quantity": 1}]}
        with self._create_test_client(partner=self.partner) as test_client:
            res = test_client.post(
                f"/wishlists/{self.prod_set.id}/add_items", json=params
            )
            self.assertEqual(res.status_code, 200)
        line1 = self.prod_set.set_line_ids.filtered(
            lambda l, _id=self.prod1.id: l.product_id.id == _id
        )
        line1.sequence = 10
        # Add another line and change order
        self.assertNotIn(self.prod2, self.prod_set.mapped("set_line_ids.product_id"))
        params = {"lines": [{"product_id": self.prod2.id}]}

        with self._create_test_client(partner=self.partner) as test_client:
            res = test_client.post(
                f"/wishlists/{self.prod_set.id}/add_items", json=params
            )
        self.assertEqual(res.status_code, 200)
        before = res.json()
        line2 = self.prod_set.set_line_ids.filtered(
            lambda l, _id=self.prod2.id: l.product_id.id == _id
        )
        self.assertEqual(line1.sequence, 10)
        self.assertEqual(line2.sequence, 0)
        self.assertEqual([x["id"] for x in before["lines"]], [line2.id, line1.id])
        params = {"lines": [{"product_id": self.prod2.id, "sequence": 20}]}
        with self._create_test_client(partner=self.partner) as test_client:
            res = test_client.post(
                f"/wishlists/{self.prod_set.id}/update_items", json=params
            )

        self.assertEqual(res.status_code, 200)
        after = res.json()
        self.assertEqual(line1.sequence, 10)
        self.assertEqual(line2.sequence, 20)
        self.assertEqual([x["id"] for x in after["lines"]], [line1.id, line2.id])

    def test_delete_items(self):
        prod = self.prod_set.set_line_ids.product_id
        self.assertTrue(prod.exists())
        params = {"lines": [{"product_id": prod.id}]}
        with self._create_test_client(partner=self.partner) as test_client:
            res = test_client.post(
                f"/wishlists/{self.prod_set.id}/delete_items", json=params
            )
        self.assertEqual(res.status_code, 200)
        self.assertFalse(self.prod_set.set_line_ids)
