# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from fastapi import status
from requests import Response

from odoo.addons.shopinvader_api_cart.routers import cart_router
from odoo.addons.shopinvader_api_cart.tests.common import CommonSaleCart

from .common import WarehouseCaseCommon


class ShopinvaderApiWarehouseInCartCase(CommonSaleCart, WarehouseCaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.default_fastapi_running_user.groups_id |= cls.env.ref(
            "shopinvader_api_warehouse.shopinvader_stock_warehouse_user_group"
        )
        # Set the default warehouse for the running company

        cls.env["ir.default"].with_company(
            cls.default_fastapi_running_user.company_id
        ).set(
            "sale.order",
            "warehouse_id",
            cls.warehouse_1.id,
        )

    def test_warehouse_in_cart(self):
        self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        data = {
            "transactions": [
                {"uuid": self.trans_uuid_1, "product_id": self.product_1.id, "qty": 1}
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            response: Response = test_client.post("/current/sync", json=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        cart_data = response.json()
        self.assertIn("warehouse", cart_data)
        self.assertEqual(cart_data["warehouse"]["id"], self.warehouse_1.id)
        self.assertEqual(cart_data["warehouse"]["name"], self.warehouse_1.name)
        self.assertEqual(cart_data["warehouse"]["code"], self.warehouse_1.code)
        self.assertEqual(cart_data["warehouse"]["default"], None)
        self.assertEqual(
            cart_data["warehouse"]["address"], self.warehouse_1.partner_id.street
        )
        self.assertEqual(
            cart_data["warehouse"]["city"], self.warehouse_1.partner_id.city
        )
        self.assertEqual(cart_data["warehouse"]["zip"], self.warehouse_1.partner_id.zip)
        self.assertEqual(
            cart_data["warehouse"]["country"],
            self.warehouse_1.partner_id.country_id.name,
        )
        self.assertEqual(
            cart_data["warehouse"]["phone"], self.warehouse_1.partner_id.phone
        )
        self.assertEqual(
            cart_data["warehouse"]["email"], self.warehouse_1.partner_id.email
        )

    def test_change_warehouse_in_cart(self):
        self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        data = {
            "transactions": [
                {"uuid": self.trans_uuid_1, "product_id": self.product_1.id, "qty": 1}
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            response: Response = test_client.post("/current/sync", json=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        cart_data = response.json()
        self.assertIn("warehouse", cart_data)
        self.assertEqual(cart_data["warehouse"]["id"], self.warehouse_1.id)

        # Now change the warehouse
        data["warehouse_id"] = self.warehouse_2.id
        with self._create_test_client(router=cart_router) as test_client:
            response: Response = test_client.post(
                f"/{cart_data['uuid']}/update", json=data
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart_data = response.json()
        self.assertIn("warehouse", cart_data)
        self.assertEqual(cart_data["warehouse"]["id"], self.warehouse_2.id)
        self.assertEqual(cart_data["warehouse"]["name"], self.warehouse_2.name)
        self.assertEqual(cart_data["warehouse"]["code"], self.warehouse_2.code)
        self.assertEqual(cart_data["warehouse"]["default"], None)
        self.assertEqual(
            cart_data["warehouse"]["address"], self.warehouse_2.partner_id.street
        )
        self.assertEqual(
            cart_data["warehouse"]["city"], self.warehouse_2.partner_id.city
        )
        self.assertEqual(cart_data["warehouse"]["zip"], self.warehouse_2.partner_id.zip)
        self.assertEqual(
            cart_data["warehouse"]["country"],
            self.warehouse_2.partner_id.country_id.name,
        )
        self.assertEqual(
            cart_data["warehouse"]["phone"], self.warehouse_2.partner_id.phone
        )
        self.assertEqual(
            cart_data["warehouse"]["email"], self.warehouse_2.partner_id.email
        )

    def test_warehouse_becomes_default_for_partner_after_confirm(self):
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        partner = self.default_fastapi_authenticated_partner
        self.assertFalse(partner.shopinvader_default_warehouse_id)
        data = {
            "transactions": [
                {"uuid": self.trans_uuid_1, "product_id": self.product_1.id, "qty": 1}
            ],
        }
        with self._create_test_client(router=cart_router) as test_client:
            response: Response = test_client.post("/current/sync", json=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(partner.shopinvader_default_warehouse_id)
        cart_data = response.json()

        with self._create_test_client(router=cart_router) as test_client:
            response: Response = test_client.post(
                f"/{cart_data['uuid']}/update",
                json={"warehouse_id": self.warehouse_2.id},
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(partner.shopinvader_default_warehouse_id)

        # Confirm the cart
        so.action_confirm_cart()

        self.assertEqual(partner.shopinvader_default_warehouse_id, self.warehouse_2)
