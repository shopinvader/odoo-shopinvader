# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from fastapi import status
from requests import Response

from odoo.addons.shopinvader_api_customer.routers.customer import customer_router

from ..routers.warehouse import warehouse_router
from .common import WarehouseCaseCommon


class ShopinvaderApiWarehouseCustomer(WarehouseCaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "FastAPI Warehouse Demo",
                "email": "warehouse@example.com",
            }
        )

        cls.default_fastapi_running_user = cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref(
                                "shopinvader_api_security_sale."
                                "shopinvader_sale_user_group"
                            ).id,
                            cls.env.ref(
                                "shopinvader_api_warehouse."
                                "shopinvader_stock_warehouse_user_group"
                            ).id,
                        ],
                    )
                ],
            }
        )

        # Run as root here sadly, just like in shopinvader_api_customer tests
        cls.default_fastapi_authenticated_partner = cls.partner

    def test_change_customer_default_warehouse(self):
        data = {
            "default_warehouse_id": self.warehouse_1.id,
        }
        with self._create_test_client(router=customer_router) as test_client:
            response: Response = test_client.post("/customer", json=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        customer_data = response.json()

        self.assertIn("default_warehouse", customer_data)
        self.assertEqual(customer_data["default_warehouse"]["id"], self.warehouse_1.id)
        self.assertEqual(
            customer_data["default_warehouse"]["name"], self.warehouse_1.name
        )
        self.assertEqual(
            customer_data["default_warehouse"]["code"], self.warehouse_1.code
        )
        self.assertEqual(customer_data["default_warehouse"]["default"], True)
        self.assertEqual(
            customer_data["default_warehouse"]["address"],
            self.warehouse_1.partner_id.street,
        )
        self.assertEqual(
            customer_data["default_warehouse"]["city"],
            self.warehouse_1.partner_id.city,
        )
        self.assertEqual(
            customer_data["default_warehouse"]["zip"],
            self.warehouse_1.partner_id.zip,
        )
        self.assertEqual(
            customer_data["default_warehouse"]["country"],
            self.warehouse_1.partner_id.country_id.name,
        )
        self.assertEqual(
            customer_data["default_warehouse"]["phone"],
            self.warehouse_1.partner_id.phone,
        )
        self.assertEqual(
            self.partner.shopinvader_default_warehouse_id.id, self.warehouse_1.id
        )

        with self._create_test_client(router=warehouse_router) as test_client:
            response: Response = test_client.get("/warehouses")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        warehouses_data = response.json()
        # We are running as root here, so we should see all warehouses
        self.assertEqual(warehouses_data["count"], 4)

        default_warehouse_data = warehouses_data["items"][0]
        default_warehouse = self.env.ref("stock.warehouse0")
        self.assertEqual(default_warehouse_data["name"], default_warehouse.name)
        self.assertEqual(default_warehouse_data["code"], default_warehouse.code)
        self.assertEqual(default_warehouse_data["default"], False)

        default_warehouse_2_data = warehouses_data["items"][1]
        default_warehouse_2 = self.env["stock.warehouse"].search(
            [("code", "=", "My Co")]
        )
        self.assertEqual(default_warehouse_2_data["name"], default_warehouse_2.name)
        self.assertEqual(default_warehouse_2_data["code"], default_warehouse_2.code)
        self.assertEqual(default_warehouse_2_data["default"], False)

        warehouse_1_data = warehouses_data["items"][2]
        self.assertEqual(warehouse_1_data["name"], self.warehouse_1.name)
        self.assertEqual(warehouse_1_data["code"], self.warehouse_1.code)
        self.assertEqual(warehouse_1_data["default"], True)

        warehouse_2_data = warehouses_data["items"][3]
        self.assertEqual(warehouse_2_data["name"], self.warehouse_2.name)
        self.assertEqual(warehouse_2_data["code"], self.warehouse_2.code)
        self.assertEqual(warehouse_2_data["default"], False)
