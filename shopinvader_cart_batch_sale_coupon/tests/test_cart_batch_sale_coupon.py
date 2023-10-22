from contextlib import contextmanager

from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase


@contextmanager
def patch_count_rcl_calls(self):
    so_cls = self.env["sale.order"].__class__
    calls = {
        "count": 0,
    }
    old_rcl = so_cls.recompute_coupon_lines

    def new_rcl(*args, **kwargs):
        nonlocal calls
        calls["count"] += 1
        return old_rcl(*args, **kwargs)

    so_cls.recompute_coupon_lines = new_rcl
    try:
        yield calls
    finally:
        so_cls.recompute_coupon_lines = old_rcl


class TestCart(CommonConnectedCartCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cart_product_0 = cls.env.ref("product.product_product_24")
        cls.cart_product_1 = cls.env.ref("product.product_product_25")
        cls.cart_product_new = cls.env.ref("product.product_product_27")

    def test_cart_add_items_coupon_recompute(self):
        with patch_count_rcl_calls(self) as calls:
            self.service.dispatch(
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
                    ],
                    "skip_coupon_recompute": False,
                },
            )["data"]

        self.assertEquals(calls["count"], 1)

    def test_cart_update_items_coupon_recompute(self):
        cart = self.service.dispatch(
            "search",
        )["data"]

        with patch_count_rcl_calls(self) as calls:
            self.service.dispatch(
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
                    ],
                    "skip_coupon_recompute": False,
                },
            )["data"]
        self.assertEquals(calls["count"], 1)

    def test_cart_delete_items_coupon_recompute(self):
        cart = self.service.dispatch(
            "search",
        )["data"]

        with patch_count_rcl_calls(self) as calls:
            self.service.dispatch(
                "delete_items",
                params={
                    "batch": [
                        {
                            "item_id": cart["lines"]["items"][0]["id"],
                        },
                        {
                            "item_id": cart["lines"]["items"][1]["id"],
                        },
                    ],
                    "skip_coupon_recompute": False,
                },
            )["data"]
        self.assertEquals(calls["count"], 1)

    def test_cart_add_items_skip_coupon_recompute(self):
        with patch_count_rcl_calls(self) as calls:
            self.service.dispatch(
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
                    ],
                    "skip_coupon_recompute": True,
                },
            )["data"]

        self.assertEquals(calls["count"], 0)

    def test_cart_update_items_skip_coupon_recompute(self):
        cart = self.service.dispatch(
            "search",
        )["data"]

        with patch_count_rcl_calls(self) as calls:
            self.service.dispatch(
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
                    ],
                    "skip_coupon_recompute": True,
                },
            )["data"]
        self.assertEquals(calls["count"], 0)

    def test_cart_delete_items_skip_coupon_recompute(self):
        cart = self.service.dispatch(
            "search",
        )["data"]

        with patch_count_rcl_calls(self) as calls:
            self.service.dispatch(
                "delete_items",
                params={
                    "batch": [
                        {
                            "item_id": cart["lines"]["items"][0]["id"],
                        },
                        {
                            "item_id": cart["lines"]["items"][1]["id"],
                        },
                    ],
                    "skip_coupon_recompute": True,
                },
            )["data"]
        self.assertEquals(calls["count"], 0)
