# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo_test_helper import FakeModelLoader

from odoo.addons.shopinvader_api_cart.routers import cart_router
from odoo.addons.shopinvader_api_cart.tests.common import CommonSaleCart


class TestSaleCartOption(CommonSaleCart):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()

        from .models import SaleOrderLine, ShopinvaderApiCartRouterHelper

        cls.loader.update_registry((SaleOrderLine, ShopinvaderApiCartRouterHelper))

        cls.backup_extendable_registry()

        from .schemas import SaleLineOptions  # noqa

        # /!\ THIS IS IMPORTANT when using FakeModelLoader, otherwise we get some
        # TypeError: super(type, obj): obj must be an instance or subtype of type
        # when calling schemas super():
        cls.reset_extendable_registry()
        cls.init_extendable_registry()

    @classmethod
    def tearDownClass(cls):
        cls.restore_extendable_registry()
        cls.loader.restore_registry()
        super().tearDownClass()

    def test_cart_no_options(self) -> None:
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        data = {
            "transactions": [
                {
                    "uuid": self.trans_uuid_1,
                    "product_id": self.product_1.id,
                    "qty": 1,
                },
                {
                    "uuid": self.trans_uuid_2,
                    "product_id": self.product_2.id,
                    "qty": 4,
                },
                {
                    "uuid": self.trans_uuid_3,
                    "product_id": self.product_1.id,
                    "qty": 2,
                },
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            response = test_client.post(f"/{so.uuid}/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201, response.text)

        data = response.json()
        self.assertEqual(data["uuid"], so.uuid)
        self.assertEqual(len(data["lines"]), 2)

        lines = data["lines"]
        self.assertEqual(lines[0]["qty"], 3)
        self.assertEqual(lines[0]["product_id"], self.product_1.id)
        self.assertEqual(lines[0]["options"]["engraving"], None)

        self.assertEqual(lines[1]["qty"], 4)
        self.assertEqual(lines[1]["product_id"], self.product_2.id)
        self.assertEqual(lines[1]["options"]["engraving"], None)

    def test_cart_different_options(self) -> None:
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        data = {
            "transactions": [
                {
                    "uuid": self.trans_uuid_1,
                    "product_id": self.product_1.id,
                    "qty": 1,
                    "options": {"engraving": "test1"},
                },
                {
                    "uuid": self.trans_uuid_2,
                    "product_id": self.product_2.id,
                    "qty": 4,
                    "options": {"engraving": "test2"},
                },
                {
                    "uuid": self.trans_uuid_3,
                    "product_id": self.product_1.id,
                    "qty": 2,
                    "options": {"engraving": "test3"},
                },
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            response = test_client.post(f"/{so.uuid}/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201, response.text)

        data = response.json()
        self.assertEqual(data["uuid"], so.uuid)
        self.assertEqual(len(data["lines"]), 3)

        lines = data["lines"]
        self.assertEqual(lines[0]["qty"], 1)
        self.assertEqual(lines[0]["product_id"], self.product_1.id)
        self.assertEqual(lines[0]["options"]["engraving"], "test1")

        self.assertEqual(lines[1]["qty"], 4)
        self.assertEqual(lines[1]["product_id"], self.product_2.id)
        self.assertEqual(lines[1]["options"]["engraving"], "test2")

        self.assertEqual(lines[2]["qty"], 2)
        self.assertEqual(lines[2]["product_id"], self.product_1.id)
        self.assertEqual(lines[2]["options"]["engraving"], "test3")

    def test_cart_same_options(self) -> None:
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        data = {
            "transactions": [
                {
                    "uuid": self.trans_uuid_1,
                    "product_id": self.product_1.id,
                    "qty": 1,
                    "options": {"engraving": "test"},
                },
                {
                    "uuid": self.trans_uuid_2,
                    "product_id": self.product_2.id,
                    "qty": 4,
                    "options": {"engraving": "test"},
                },
                {
                    "uuid": self.trans_uuid_3,
                    "product_id": self.product_1.id,
                    "qty": 2,
                    "options": {"engraving": "test"},
                },
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            response = test_client.post(f"/{so.uuid}/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201, response.text)

        data = response.json()
        self.assertEqual(data["uuid"], so.uuid)
        self.assertEqual(len(data["lines"]), 2)

        lines = data["lines"]
        self.assertEqual(lines[0]["qty"], 3)
        self.assertEqual(lines[0]["product_id"], self.product_1.id)
        self.assertEqual(lines[0]["options"]["engraving"], "test")

        self.assertEqual(lines[1]["qty"], 4)
        self.assertEqual(lines[1]["product_id"], self.product_2.id)
        self.assertEqual(lines[1]["options"]["engraving"], "test")

    def test_cart_two_options(self) -> None:
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        data = {
            "transactions": [
                {
                    "uuid": self.trans_uuid_1,
                    "product_id": self.product_1.id,
                    "qty": 1,
                    "options": {"engraving": "test"},
                },
                {
                    "uuid": self.trans_uuid_2,
                    "product_id": self.product_2.id,
                    "qty": 4,
                    "options": {"engraving": "test"},
                },
                {
                    "uuid": self.trans_uuid_3,
                    "product_id": self.product_1.id,
                    "qty": 2,
                    "options": {"engraving": "test"},
                },
                {
                    "uuid": self.trans_uuid_4,
                    "product_id": self.product_1.id,
                    "qty": 5,
                    "options": {"engraving": "test", "special": True},
                },
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            response = test_client.post(f"/{so.uuid}/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201, response.text)

        data = response.json()
        self.assertEqual(data["uuid"], so.uuid)
        self.assertEqual(len(data["lines"]), 3)

        lines = data["lines"]
        self.assertEqual(lines[0]["qty"], 3)
        self.assertEqual(lines[0]["product_id"], self.product_1.id)
        self.assertEqual(lines[0]["options"]["engraving"], "test")
        self.assertFalse(lines[0]["options"]["special"])

        self.assertEqual(lines[1]["qty"], 4)
        self.assertEqual(lines[1]["product_id"], self.product_2.id)
        self.assertEqual(lines[1]["options"]["engraving"], "test")
        self.assertFalse(lines[1]["options"]["special"])

        self.assertEqual(lines[2]["qty"], 5)
        self.assertEqual(lines[2]["product_id"], self.product_1.id)
        self.assertEqual(lines[2]["options"]["engraving"], "test")
        self.assertTrue(lines[2]["options"]["special"])

    def test_cart_successive_transactions(self) -> None:
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        for tx in [
            {
                "uuid": self.trans_uuid_1,
                "product_id": self.product_1.id,
                "qty": 1,
                "options": {"engraving": "test"},
            },
            {
                "uuid": self.trans_uuid_2,
                "product_id": self.product_2.id,
                "qty": 4,
                "options": {"engraving": "test"},
            },
            {
                "uuid": self.trans_uuid_3,
                "product_id": self.product_1.id,
                "qty": 2,
                "options": {"engraving": "test"},
            },
            {
                "uuid": self.trans_uuid_4,
                "product_id": self.product_1.id,
                "qty": 5,
                "options": {"engraving": "test", "special": True},
            },
        ]:
            data = {"transactions": [tx]}
            with self._create_test_client(router=cart_router) as test_client:
                response = test_client.post(
                    f"/{so.uuid}/sync", content=json.dumps(data)
                )
            self.assertEqual(response.status_code, 201, response.text)

        data = response.json()
        self.assertEqual(data["uuid"], so.uuid)
        self.assertEqual(len(data["lines"]), 3)

        lines = data["lines"]
        self.assertEqual(lines[0]["qty"], 3)
        self.assertEqual(lines[0]["product_id"], self.product_1.id)
        self.assertEqual(lines[0]["options"]["engraving"], "test")
        self.assertFalse(lines[0]["options"]["special"])

        self.assertEqual(lines[1]["qty"], 4)
        self.assertEqual(lines[1]["product_id"], self.product_2.id)
        self.assertEqual(lines[1]["options"]["engraving"], "test")
        self.assertFalse(lines[1]["options"]["special"])

        self.assertEqual(lines[2]["qty"], 5)
        self.assertEqual(lines[2]["product_id"], self.product_1.id)
        self.assertEqual(lines[2]["options"]["engraving"], "test")
        self.assertTrue(lines[2]["options"]["special"])

    def test_cart_transfer_options(self):
        so1 = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        data = {
            "transactions": [
                {
                    "uuid": self.trans_uuid_1,
                    "product_id": self.product_1.id,
                    "qty": 1,
                    "options": {"engraving": "test"},
                },
                {
                    "uuid": self.trans_uuid_2,
                    "product_id": self.product_2.id,
                    "qty": 4,
                    "options": {"engraving": "test"},
                },
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            response = test_client.post(f"/{so1.uuid}/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201, response.text)

        so2 = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        data = {
            "transactions": [
                {
                    "uuid": self.trans_uuid_3,
                    "product_id": self.product_1.id,
                    "qty": 2,
                    "options": {"engraving": "test"},
                },
                {
                    "uuid": self.trans_uuid_4,
                    "product_id": self.product_1.id,
                    "qty": 5,
                    "options": {"engraving": "test", "special": True},
                },
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            response = test_client.post(f"/{so2.uuid}/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201, response.text)

        so1._transfer_cart(so2.partner_id.id)

        with self._create_test_client(router=cart_router) as test_client:
            response = test_client.get("/")
            self.assertEqual(response.status_code, 200, response.text)

        data = response.json()
        self.assertEqual(data["uuid"], so2.uuid)
        self.assertEqual(len(data["lines"]), 3)

        lines = data["lines"]
        self.assertEqual(lines[0]["qty"], 3)
        self.assertEqual(lines[0]["product_id"], self.product_1.id)
        self.assertEqual(lines[0]["options"]["engraving"], "test")
        self.assertFalse(lines[0]["options"]["special"])

        self.assertEqual(lines[1]["qty"], 5)
        self.assertEqual(lines[1]["product_id"], self.product_1.id)
        self.assertEqual(lines[1]["options"]["engraving"], "test")
        self.assertTrue(lines[1]["options"]["special"])

        self.assertEqual(lines[2]["qty"], 4)
        self.assertEqual(lines[2]["product_id"], self.product_2.id)
        self.assertEqual(lines[2]["options"]["engraving"], "test")
        self.assertFalse(lines[2]["options"]["special"])

    def test_cart_transfer_no_options(self):
        so1 = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        data = {
            "transactions": [
                {
                    "uuid": self.trans_uuid_1,
                    "product_id": self.product_1.id,
                    "qty": 1,
                },
                {
                    "uuid": self.trans_uuid_2,
                    "product_id": self.product_2.id,
                    "qty": 4,
                },
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            response = test_client.post(f"/{so1.uuid}/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201, response.text)

        so2 = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        data = {
            "transactions": [
                {
                    "uuid": self.trans_uuid_3,
                    "product_id": self.product_1.id,
                    "qty": 2,
                },
                {
                    "uuid": self.trans_uuid_4,
                    "product_id": self.product_1.id,
                    "qty": 5,
                },
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            response = test_client.post(f"/{so2.uuid}/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201, response.text)

        so1._transfer_cart(so2.partner_id.id)

        with self._create_test_client(router=cart_router) as test_client:
            response = test_client.get("/")
            self.assertEqual(response.status_code, 200, response.text)

        data = response.json()
        self.assertEqual(data["uuid"], so2.uuid)
        self.assertEqual(len(data["lines"]), 2)

        lines = data["lines"]
        self.assertEqual(lines[0]["qty"], 8)
        self.assertEqual(lines[0]["product_id"], self.product_1.id)

        self.assertEqual(lines[1]["qty"], 4)
        self.assertEqual(lines[1]["product_id"], self.product_2.id)
