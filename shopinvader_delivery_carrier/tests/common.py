# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo_test_helper import FakeModelLoader

from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase


class CommonCarrierCase(CommonConnectedCartCase):
    @classmethod
    def setUpClass(cls):
        super(CommonCarrierCase, cls).setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()

        from .models import OtherCarrier

        cls.loader.update_registry((OtherCarrier,))

        cls.free_carrier = cls.env.ref("delivery.free_delivery_carrier")
        cls.free_carrier.code = "FREE"
        cls.free_carrier.description = "delivery in 5 days"

        cls.poste_carrier = cls.env.ref("delivery.delivery_carrier")
        cls.poste_carrier.code = "POSTE"
        cls.poste_carrier.description = "delivery in 2 days"

        cls.other_carrier = cls.env["delivery.carrier"].create(
            {
                "name": "Other carrier",
                "code": "OTHER",
                "description": "delivery computed by the carrier",
                "delivery_type": "other",
                "product_id": cls.env["product.product"]
                .create(
                    {
                        "name": "Other delivery",
                        "default_code": "OTHER_DELIVERY",
                        "type": "service",
                        "categ_id": cls.env.ref(
                            "delivery.product_category_deliveries"
                        ).id,
                        "sale_ok": False,
                        "purchase_ok": False,
                        "list_price": "0.0",
                        "invoice_policy": "order",
                    }
                )
                .id,
            }
        )
        cls.other_carrier.description = "delivery computed by the carrier"

        cls.product_1 = cls.env.ref("product.product_product_4b")
        cls.precision = 2

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def extract_cart(self, response):
        self.shopinvader_session["cart_id"] = response["set_session"]["cart_id"]
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

    def update_carrier_shipping_costs(self):
        return self.extract_cart(self.service.dispatch("update_carrier_shipping_costs"))

    def _set_carrier(self, carrier):
        response = self.service.dispatch(
            "set_carrier", params={"carrier_id": carrier.id}
        )
        self.assertEqual(self.cart.carrier_id.id, carrier.id)
        return response["data"]

    def _apply_delivery_method(self, carrier):
        response = self.service.dispatch(
            "apply_delivery_method", params={"carrier": {"id": carrier.id}}
        )
        self.assertEqual(self.cart.carrier_id.id, carrier.id)
        return response["data"]

    def _apply_carrier_and_assert_set(self):
        cart = self._set_carrier(self.poste_carrier)
        self.assertEqual(cart["shipping"]["amount"]["total"], 20)
        return cart
