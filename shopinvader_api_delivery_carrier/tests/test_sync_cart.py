# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
import uuid

from requests import Response

from odoo.tests.common import tagged

from odoo.addons.shopinvader_api_cart.routers import cart_router

from .common import TestShopinvaderDeliveryCarrierCommon


@tagged("post_install", "-at_install")
class TestSyncCart(TestShopinvaderDeliveryCarrierCommon):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_with_rights.groups_id = [
            (
                6,
                0,
                [
                    cls.env.ref(
                        "shopinvader_api_security_sale.shopinvader_sale_user_group"
                    ).id,
                ],
            )
        ]
        cls.trans_uuid_1 = str(uuid.uuid4())

    def _set_carrier(self, carrier):
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "carrier_id": carrier.id,
            }
            response: Response = test_client.post(
                "/set_carrier", content=json.dumps(data)
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.cart.carrier_id.id, carrier.id)
        return response.json()

    def _apply_carrier_and_assert_set(self):
        cart = self._set_carrier(self.poste_carrier)
        self.assertEqual(cart["delivery"]["amount"]["total"], 24)

    def test_reset_carrier_on_add_item(self):
        """
        Add a new item to the cart.
        Check that the carrier was removed.
        """
        self._apply_carrier_and_assert_set()
        product = self.env.ref("product.product_product_4")
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {"uuid": self.trans_uuid_1, "product_id": product.id, "qty": 1}
                ]
            }
            response: Response = test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        res = response.json()
        self.assertEqual(
            set(self.cart.order_line.mapped("product_id.id")),
            {self.product_1.id, product.id},
        )

        self.assertEqual(res["delivery"]["amount"]["total"], 0)
        self.assertFalse(res["delivery"]["selected_carrier"])

    def test_reset_carrier_on_update_item(self):
        """
        Update the item in the cart.
        Check that the carrier was removed.
        """
        self._apply_carrier_and_assert_set()
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {
                        "uuid": self.trans_uuid_1,
                        "product_id": self.cart.order_line[0].product_id.id,
                        "qty": 3,
                    }
                ]
            }
            response: Response = test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        res = response.json()
        self.assertEqual(self.cart.order_line[0].product_uom_qty, 4)
        self.assertEqual(res["delivery"]["amount"]["total"], 0)
        self.assertFalse(res["delivery"]["selected_carrier"])

    def test_reset_carrier_on_delete_item(self):
        """
        Delete the item in the cart.
        Check that the carrier was removed.
        """
        self._apply_carrier_and_assert_set()
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {
                        "uuid": self.trans_uuid_1,
                        "product_id": self.cart.order_line[0].product_id.id,
                        "qty": -self.cart.order_line[0].product_uom_qty,
                    }
                ]
            }
            response: Response = test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        res = response.json()
        self.assertFalse(self.cart.order_line)
        self.assertEqual(res["delivery"]["amount"]["total"], 0)
        self.assertFalse(res["delivery"]["selected_carrier"])
