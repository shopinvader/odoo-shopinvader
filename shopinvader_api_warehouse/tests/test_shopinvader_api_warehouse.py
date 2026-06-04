# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from fastapi import status
from requests import Response

from ..routers.warehouse import warehouse_router
from .common import WarehouseCaseCommon


class ShopinvaderApiWarehouse(WarehouseCaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "FastAPI Warehouse Demo",
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
        cls.default_fastapi_authenticated_partner = cls.partner.with_user(
            cls.default_fastapi_running_user
        )

    def test_search_warehouse(self):
        self.partner.shopinvader_default_warehouse_id = self.warehouse_2

        with self._create_test_client(router=warehouse_router) as test_client:
            response: Response = test_client.get("/warehouses")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        warehouses_data = response.json()
        self.assertEqual(warehouses_data["count"], 3)
        default_warehouse_data = warehouses_data["items"][0]
        default_warehouse = self.env.ref("stock.warehouse0")
        self.assertEqual(default_warehouse_data["name"], default_warehouse.name)
        self.assertEqual(default_warehouse_data["code"], default_warehouse.code)
        self.assertEqual(default_warehouse_data["default"], False)
        self.assertEqual(
            default_warehouse_data["address"], default_warehouse.partner_id.street
        )
        self.assertEqual(
            default_warehouse_data["city"], default_warehouse.partner_id.city
        )
        self.assertEqual(
            default_warehouse_data["zip"], default_warehouse.partner_id.zip
        )
        self.assertEqual(
            default_warehouse_data["country"],
            default_warehouse.partner_id.country_id.name,
        )
        self.assertEqual(
            default_warehouse_data["phone"], default_warehouse.partner_id.phone
        )

        warehouse_1_data = warehouses_data["items"][1]
        self.assertEqual(warehouse_1_data["name"], self.warehouse_1.name)
        self.assertEqual(warehouse_1_data["code"], self.warehouse_1.code)
        self.assertEqual(warehouse_1_data["default"], False)
        self.assertEqual(
            warehouse_1_data["address"], self.warehouse_1.partner_id.street
        )
        self.assertEqual(warehouse_1_data["city"], self.warehouse_1.partner_id.city)
        self.assertEqual(warehouse_1_data["zip"], self.warehouse_1.partner_id.zip)
        self.assertEqual(
            warehouse_1_data["country"],
            self.warehouse_1.partner_id.country_id.name,
        )
        self.assertEqual(warehouse_1_data["phone"], self.warehouse_1.partner_id.phone)
        warehouse_2_data = warehouses_data["items"][2]
        self.assertEqual(warehouse_2_data["name"], self.warehouse_2.name)
        self.assertEqual(warehouse_2_data["code"], self.warehouse_2.code)
        self.assertEqual(warehouse_2_data["default"], True)
        self.assertEqual(
            warehouse_2_data["address"], self.warehouse_2.partner_id.street
        )
        self.assertEqual(warehouse_2_data["city"], self.warehouse_2.partner_id.city)
        self.assertEqual(warehouse_2_data["zip"], self.warehouse_2.partner_id.zip)
        self.assertEqual(
            warehouse_2_data["country"],
            self.warehouse_2.partner_id.country_id.name,
        )
        self.assertEqual(warehouse_2_data["phone"], self.warehouse_2.partner_id.phone)
