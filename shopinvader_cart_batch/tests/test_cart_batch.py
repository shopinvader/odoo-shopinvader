from werkzeug.exceptions import NotFound

from odoo.exceptions import MissingError

from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase


class TestCart(CommonConnectedCartCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cart_product_0 = cls.env.ref("product.product_product_24")
        cls.cart_product_1 = cls.env.ref("product.product_product_25")
        cls.cart_product_new = cls.env.ref("product.product_product_27")

    def test_cart_add_items(self):
        cart = self.service.dispatch(
            "search",
        )["data"]

        self.assertEquals(cart["lines"]["count"], 5)
        self.assertEquals(
            cart["lines"]["items"][0]["product"]["id"], self.cart_product_0.id
        )
        self.assertEquals(cart["lines"]["items"][0]["qty"], 3)
        self.assertEquals(
            cart["lines"]["items"][1]["product"]["id"], self.cart_product_1.id
        )
        self.assertEquals(cart["lines"]["items"][1]["qty"], 2)

        cart = self.service.dispatch(
            "add_items",
            params={
                "batch": [
                    {
                        "product_id": self.cart_product_0.id,
                        "item_qty": 10,
                    },
                    {
                        "product_id": self.cart_product_1.id,
                        "item_qty": 20,
                    },
                    {
                        "product_id": self.cart_product_new.id,
                        "item_qty": 5,
                    },
                ]
            },
        )["data"]

        self.assertEquals(cart["lines"]["count"], 40)
        self.assertEquals(
            cart["lines"]["items"][0]["product"]["id"], self.cart_product_0.id
        )
        self.assertEquals(cart["lines"]["items"][0]["qty"], 13)
        self.assertEquals(
            cart["lines"]["items"][1]["product"]["id"], self.cart_product_1.id
        )
        self.assertEquals(cart["lines"]["items"][1]["qty"], 22)
        self.assertEquals(
            cart["lines"]["items"][2]["product"]["id"], self.cart_product_new.id
        )
        self.assertEquals(cart["lines"]["items"][2]["qty"], 5)

    def test_cart_update_items(self):
        cart = self.service.dispatch(
            "search",
        )["data"]

        self.assertEquals(cart["lines"]["count"], 5)
        self.assertEquals(
            cart["lines"]["items"][0]["product"]["id"], self.cart_product_0.id
        )
        self.assertEquals(cart["lines"]["items"][0]["qty"], 3)
        self.assertEquals(
            cart["lines"]["items"][1]["product"]["id"], self.cart_product_1.id
        )
        self.assertEquals(cart["lines"]["items"][1]["qty"], 2)

        cart = self.service.dispatch(
            "update_items",
            params={
                "batch": [
                    {
                        "item_id": cart["lines"]["items"][0]["id"],
                        "item_qty": 10,
                    },
                    {
                        "item_id": cart["lines"]["items"][1]["id"],
                        "item_qty": 20,
                    },
                ]
            },
        )["data"]

        self.assertEquals(cart["lines"]["count"], 30)
        self.assertEquals(
            cart["lines"]["items"][0]["product"]["id"], self.cart_product_0.id
        )
        self.assertEquals(cart["lines"]["items"][0]["qty"], 10)
        self.assertEquals(
            cart["lines"]["items"][1]["product"]["id"], self.cart_product_1.id
        )
        self.assertEquals(cart["lines"]["items"][1]["qty"], 20)

    def test_cart_delete_items(self):
        cart = self.service.dispatch(
            "search",
        )["data"]

        self.assertEquals(cart["lines"]["count"], 5)
        self.assertEquals(
            cart["lines"]["items"][0]["product"]["id"], self.cart_product_0.id
        )
        self.assertEquals(cart["lines"]["items"][0]["qty"], 3)
        self.assertEquals(
            cart["lines"]["items"][1]["product"]["id"], self.cart_product_1.id
        )
        self.assertEquals(cart["lines"]["items"][1]["qty"], 2)

        cart = self.service.dispatch(
            "delete_items",
            params={
                "batch": [
                    {
                        "item_id": cart["lines"]["items"][0]["id"],
                    },
                    {
                        "item_id": cart["lines"]["items"][1]["id"],
                    },
                ]
            },
        )["data"]

        self.assertEquals(cart["lines"]["count"], 0)

    def test_cart_add_items_error(self):
        cart = self.service.dispatch(
            "search",
        )["data"]

        self.assertEquals(cart["lines"]["count"], 5)
        self.assertEquals(
            cart["lines"]["items"][0]["product"]["id"], self.cart_product_0.id
        )
        self.assertEquals(cart["lines"]["items"][0]["qty"], 3)
        self.assertEquals(
            cart["lines"]["items"][1]["product"]["id"], self.cart_product_1.id
        )
        self.assertEquals(cart["lines"]["items"][1]["qty"], 2)

        with self.assertRaisesRegexp(
            MissingError,
            "Error while adding item -1 to cart: Record does not exist or has been deleted.",
        ) as e, self.env.cr.savepoint():
            cart = self.service.dispatch(
                "add_items",
                params={
                    "batch": [
                        {
                            "product_id": self.cart_product_0.id,
                            "item_qty": 1,
                        },
                        {
                            "product_id": -1,
                            "item_qty": 2,
                        },
                        {
                            "product_id": self.cart_product_new.id,
                            "item_qty": 5,
                        },
                    ]
                },
            )["data"]
        self.assertEquals(e.exception.rest_json_info["product_id"], -1)

        cart = self.service.dispatch(
            "search",
        )["data"]

        self.assertEquals(cart["lines"]["count"], 5)
        self.assertEquals(
            cart["lines"]["items"][0]["product"]["id"], self.cart_product_0.id
        )
        self.assertEquals(cart["lines"]["items"][0]["qty"], 3)
        self.assertEquals(
            cart["lines"]["items"][1]["product"]["id"], self.cart_product_1.id
        )
        self.assertEquals(cart["lines"]["items"][1]["qty"], 2)

    def test_cart_update_items_error(self):
        cart = self.service.dispatch(
            "search",
        )["data"]

        self.assertEquals(cart["lines"]["count"], 5)
        self.assertEquals(
            cart["lines"]["items"][0]["product"]["id"], self.cart_product_0.id
        )
        self.assertEquals(cart["lines"]["items"][0]["qty"], 3)
        self.assertEquals(
            cart["lines"]["items"][1]["product"]["id"], self.cart_product_1.id
        )
        self.assertEquals(cart["lines"]["items"][1]["qty"], 2)

        with self.assertRaisesRegexp(
            NotFound,
            "404 Not Found: Error while updating item -1 to cart: "
            "404 Not Found: No cart item found with id -1",
        ) as e, self.env.cr.savepoint():
            cart = self.service.dispatch(
                "update_items",
                params={
                    "batch": [
                        {
                            "item_id": cart["lines"]["items"][0]["id"],
                            "item_qty": 10,
                        },
                        {
                            "item_id": -1,
                            "item_qty": 20,
                        },
                    ]
                },
            )["data"]
        self.assertEquals(e.exception.rest_json_info["item_id"], -1)

        cart = self.service.dispatch(
            "search",
        )["data"]

        self.assertEquals(cart["lines"]["count"], 5)
        self.assertEquals(
            cart["lines"]["items"][0]["product"]["id"], self.cart_product_0.id
        )
        self.assertEquals(cart["lines"]["items"][0]["qty"], 3)
        self.assertEquals(
            cart["lines"]["items"][1]["product"]["id"], self.cart_product_1.id
        )
        self.assertEquals(cart["lines"]["items"][1]["qty"], 2)

    def test_cart_delete_items_error(self):
        cart = self.service.dispatch(
            "search",
        )["data"]

        self.assertEquals(cart["lines"]["count"], 5)
        self.assertEquals(
            cart["lines"]["items"][0]["product"]["id"], self.cart_product_0.id
        )
        self.assertEquals(cart["lines"]["items"][0]["qty"], 3)
        self.assertEquals(
            cart["lines"]["items"][1]["product"]["id"], self.cart_product_1.id
        )
        self.assertEquals(cart["lines"]["items"][1]["qty"], 2)

        cart = self.service.dispatch(
            "delete_items",
            params={
                "batch": [
                    {
                        "item_id": cart["lines"]["items"][0]["id"],
                    },
                    {
                        "item_id": -1,
                    },
                ]
            },
        )["data"]

        # Delete do not raises if item not found
        cart = self.service.dispatch(
            "search",
        )["data"]

        self.assertEquals(cart["lines"]["count"], 2)
        self.assertEquals(
            cart["lines"]["items"][0]["product"]["id"], self.cart_product_1.id
        )
        self.assertEquals(cart["lines"]["items"][0]["qty"], 2)
