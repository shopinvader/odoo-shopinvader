# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from fastapi import status
from fastapi.responses import Response

from odoo.addons.shopinvader_api_warehouse.routers.warehouse import warehouse_router
from odoo.addons.shopinvader_api_warehouse.tests.common import WarehouseCaseCommon


class TestShopinvaderApiWarehouseSaleChannel(WarehouseCaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.sale_channel = cls.env["sale.channel"].create(
            {
                "name": "Test Sale Channel",
            }
        )
        cls.sale_channel2 = cls.env["sale.channel"].create(
            {
                "name": "Test Sale Channel 2",
            }
        )

        cls.warehouse_1.sale_channel_ids = [(4, cls.sale_channel.id)]
        cls.warehouse_2.sale_channel_ids = [(4, cls.sale_channel2.id)]
        cls.env.ref("stock.warehouse0").sale_channel_ids = [
            (6, 0, (cls.sale_channel | cls.sale_channel2).ids)
        ]

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "FastAPI Warehouse Demo",
            }
        )

        cls.default_fastapi_running_user = cls.env.ref("fastapi.my_demo_app_user")
        cls.default_fastapi_running_user.groups_id |= cls.env.ref(
            "shopinvader_api_security_sale.shopinvader_sale_user_group"
        ) | cls.env.ref(
            "shopinvader_api_warehouse.shopinvader_stock_warehouse_user_group"
        )

        cls.endpoint = cls.env.ref("fastapi.fastapi_endpoint_demo")
        cls.endpoint.sale_channel_id = cls.sale_channel.id
        # We use the api_key auth method here to be able to authenticate as
        # a partner with the real dependency machinery (env creation)
        cls.endpoint.demo_auth_method = "api_key"
        cls.default_fastapi_app = cls.endpoint._get_app()
        cls.default_fastapi_dependency_overrides = (
            cls.default_fastapi_app.dependency_overrides
        )

    def test_search_warehouse_1(self):
        with self._create_test_client(router=warehouse_router) as test_client:
            response: Response = test_client.get(
                "/warehouses", headers={"api-key": "my_demo_app_user"}
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        warehouses_data = response.json()
        self.assertEqual(warehouses_data["count"], 2)
        default_warehouse_data = warehouses_data["items"][0]
        default_warehouse = self.env.ref("stock.warehouse0")
        self.assertEqual(default_warehouse_data["name"], default_warehouse.name)
        self.assertEqual(default_warehouse_data["code"], default_warehouse.code)
        self.assertEqual(default_warehouse_data["default"], None)
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
        self.assertEqual(warehouse_1_data["default"], None)
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

    def test_search_warehouse_2(self):
        self.endpoint.sale_channel_id = self.sale_channel2.id

        with self._create_test_client(router=warehouse_router) as test_client:
            response: Response = test_client.get(
                "/warehouses", headers={"api-key": "my_demo_app_user"}
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        warehouses_data = response.json()
        self.assertEqual(warehouses_data["count"], 2)
        default_warehouse_data = warehouses_data["items"][0]
        default_warehouse = self.env.ref("stock.warehouse0")
        self.assertEqual(default_warehouse_data["name"], default_warehouse.name)
        self.assertEqual(default_warehouse_data["code"], default_warehouse.code)
        self.assertEqual(default_warehouse_data["default"], None)
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
        warehouse_2_data = warehouses_data["items"][1]
        self.assertEqual(warehouse_2_data["name"], self.warehouse_2.name)
        self.assertEqual(warehouse_2_data["code"], self.warehouse_2.code)
        self.assertEqual(warehouse_2_data["default"], None)
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
