# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from extendable import context
from fastapi import status
from requests import Response

from odoo.exceptions import MissingError
from odoo.tests.common import tagged

from odoo.addons.extendable.registry import _extendable_registries_database
from odoo.addons.fastapi.tests.common import FastAPITransactionCase

from ..routers.cart import cart_router
from ..schemas import CartTransaction

# TODO: a second test class with a user that has no rights


@tagged("post_install", "-at_install")
class TestSaleCart(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        extendable_registry = _extendable_registries_database.get(cls.env.cr.dbname)
        cls.token = context.extendable_registry.set(extendable_registry)
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.user_no_rights = cls.env["res.users"].create(
            {
                "name": "Test User Without Rights",
                "login": "user_no_rights",
            }
        )
        user_with_rights = cls.env["res.users"].create(
            {
                "name": "Test User With Rights",
                "login": "user_with_rights",
            }
        )
        user_with_rights.groups_id = [
            (4, cls.env.ref("shopinvader_api_cart.sale_cart_user_group").id)
        ]
        cls.default_fastapi_running_user = user_with_rights
        cls.default_fastapi_authenticated_partner = (
            cls.env["res.partner"]
            .with_user(user_with_rights)
            .create({"name": "FastAPI Cart Demo"})
        )
        cls.default_fastapi_router = cart_router

        cls.partner_in_user_no_rights = cls.env(user=cls.user_no_rights)[
            "res.partner"
        ].browse(cls.default_fastapi_authenticated_partner.id)

        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "product_1",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "product_2",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )

    @classmethod
    def tearDownClass(cls) -> None:
        context.extendable_registry.reset(cls.token)
        super().tearDownClass()

    # @contextmanager
    def _create_unauthenticated_user_client(self):
        return self._create_test_client(
            user=self.user_no_rights, partner=self.partner_in_user_no_rights
        )

    def test_get_authenticated_no_cart_no_uuid(self) -> None:
        with self._create_test_client(router=cart_router) as test_client:
            response: Response = test_client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.json(), {})

    # TODO: fix. Up to now the user has Admin rights, he shouldn't
    def test_get_authenticated_no_cart_no_uuid_no_rights(self) -> None:
        with self._create_unauthenticated_user_client() as test_client:
            response: Response = test_client.get("/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_authenticated_no_cart_uuid(self) -> None:
        with self._create_test_client(router=cart_router) as test_client:
            response: Response = test_client.get("/1234")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.json(), {})

    def test_get_authenticated_cart_uuid(self) -> None:
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        with self._create_test_client(router=cart_router) as test_client:
            response: Response = test_client.get(f"/{so.uuid}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], so.id)

    def test_get_authenticated_cart_wrong_uuid(self) -> None:
        """
        Authenticated partner, wrong uuid
        We should get the last opened cart for this partner
        """
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        with self._create_test_client(router=cart_router) as test_client:
            response: Response = test_client.get("/1234")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], so.id)

    def test_get_authenticated_exists_cart_no_uuid(self) -> None:
        """
        Authenticated partner, no uuid
        We should get the last opened cart for this partner
        """
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        with self._create_test_client(router=cart_router) as test_client:
            response: Response = test_client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], so.id)

    def test_sync_authenticated_no_uuid_one_transactions_no_cart_exists(self) -> None:
        """
        Provide no uuid but at least one transaction. Since no cart exists,
        create cart.
        """
        data = {
            "transactions": [
                {"uuid": "uuid1", "product_id": self.product_1.id, "qty": 1}
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            response: Response = test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = response.json()
        self.assertTrue(response_json)
        self.assertEqual(1, len(response_json["lines"]))
        so = self.env["sale.order"].browse(response_json["id"])
        self.assertEqual("uuid1", so.applied_transaction_uuids)

    def test_sync_authenticated_no_uuid_one_transactions_cart_exists(self) -> None:
        """
        Provide no uuid but at least one transaction. Since a cart exists,
        update the cart.
        """
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        data = {
            "transactions": [
                {"uuid": "uuid1", "product_id": self.product_1.id, "qty": 1}
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            response: Response = test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = response.json()
        self.assertTrue(response_json)
        self.assertEqual(1, len(response_json["lines"]))
        self.assertEqual(so.id, response_json["id"])
        self.assertEqual("uuid1", so.applied_transaction_uuids)

    def test_sync_authenticated_wrong_uuid_one_transactions_cart_exists(self) -> None:
        """
        Provide a wrong uuid and at least one transaction. Since a cart exists,
        return the existing cart and ignore transactions
        """
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        data = {
            "transactions": [
                {"uuid": "uuid1", "product_id": self.product_1.id, "qty": 1}
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            response: Response = test_client.post(
                "/sync/1234", content=json.dumps(data)
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = response.json()
        self.assertTrue(response_json)
        self.assertEqual(0, len(response_json["lines"]))
        self.assertEqual(so.id, response_json["id"])
        self.assertFalse(so.applied_transaction_uuids)

    def test_transaction_product_not_existing(self) -> None:
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        # Generate a non existing product ID:
        product_to_remove = self.env["product.product"].create(
            {
                "name": "product to remove",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        not_existing_product_id = product_to_remove.id
        product_to_remove.unlink()
        data = {
            "transactions": [
                {"uuid": "uuid1", "product_id": not_existing_product_id, "qty": 1}
            ]
        }
        with self._create_test_client(
            router=cart_router
        ) as test_client, self.assertRaises(MissingError):
            test_client.post(f"/sync/{so.uuid}", content=json.dumps(data))

    def test_transactions(self) -> None:
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        data = {
            "transactions": [
                {"uuid": "uuid1", "product_id": self.product_1.id, "qty": 1}
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            test_client.post(f"/sync/{so.uuid}", content=json.dumps(data))
        line = so.order_line
        self.assertEqual(1, len(line))
        self.assertEqual(self.product_1, line.product_id)
        self.assertEqual(1, line.product_uom_qty)

        # Add 3 items to product
        data = {
            "transactions": [
                {"uuid": "uuid2", "product_id": self.product_1.id, "qty": 3}
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            test_client.post(f"/sync/{so.uuid}", content=json.dumps(data))
        line = so.order_line
        self.assertEqual(1, len(line))
        self.assertEqual(self.product_1, line.product_id)
        self.assertEqual(4, line.product_uom_qty)

        # New sync to remove the line
        data = {
            "transactions": [
                {"uuid": "uuid3", "product_id": self.product_1.id, "qty": -5}
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            test_client.post(f"/sync/{so.uuid}", content=json.dumps(data))
        line = so.order_line
        self.assertEqual(0, len(line))

    def test_multi_transactions_same_product(self) -> None:
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        data = {
            "transactions": [
                {"uuid": "uuid1", "product_id": self.product_1.id, "qty": 1},
                {"uuid": "uuid2", "product_id": self.product_1.id, "qty": 3},
                {"uuid": "uuid3", "product_id": self.product_1.id, "qty": -1},
                {"uuid": "uuid4", "product_id": self.product_1.id, "qty": -1},
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            test_client.post(f"/sync/{so.uuid}", content=json.dumps(data))
        line = so.order_line
        self.assertEqual(1, len(line))
        self.assertEqual(self.product_1, line.product_id)
        self.assertEqual(2, line.product_uom_qty)
        self.assertEqual(so.applied_transaction_uuids, "uuid1,uuid2,uuid3,uuid4")

    def test_multi_transactions_same_product1(self) -> None:
        # try to remove more product than qty added
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        data = {
            "transactions": [
                {"uuid": "uuid1", "product_id": self.product_1.id, "qty": 1},
                {"uuid": "uuid2", "product_id": self.product_1.id, "qty": 3},
                {"uuid": "uuid3", "product_id": self.product_1.id, "qty": -1},
                {"uuid": "uuid4", "product_id": self.product_1.id, "qty": -5},
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            test_client.post(f"/sync/{so.uuid}", content=json.dumps(data))
        line = so.order_line
        self.assertEqual(0, len(line))
        self.assertEqual(so.applied_transaction_uuids, "uuid1,uuid2,uuid3,uuid4")

    def test_multi_transactions_update_same_product(self) -> None:
        # try to remove more product than qty on existing line
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        data = {
            "transactions": [
                {"uuid": "uuid1", "product_id": self.product_1.id, "qty": 1},
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            test_client.post(f"/sync/{so.uuid}", content=json.dumps(data))
        line = so.order_line
        self.assertEqual(1, len(line))
        data = {
            "transactions": [
                {"uuid": "uuid2", "product_id": self.product_1.id, "qty": 3},
                {"uuid": "uuid3", "product_id": self.product_1.id, "qty": -100},
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            test_client.post(f"/sync/{so.uuid}", content=json.dumps(data))
        line = so.order_line
        self.assertEqual(0, len(line))
        self.assertEqual(so.applied_transaction_uuids, "uuid1,uuid2,uuid3")

    def test_multi_transactions_multi_products_all_create(self) -> None:
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        data = {
            "transactions": [
                {"uuid": "uuid1", "product_id": self.product_1.id, "qty": 1},
                {"uuid": "uuid2", "product_id": self.product_2.id, "qty": 3},
                {"uuid": "uuid3", "product_id": self.product_1.id, "qty": 3},
                {"uuid": "uuid4", "product_id": self.product_2.id, "qty": -1},
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            test_client.post(f"/sync/{so.uuid}", content=json.dumps(data))
        lines = so.order_line
        self.assertEqual(2, len(lines))
        line_product_1_id = lines.filtered(
            lambda l, product=self.product_1: l.product_id == product
        )
        self.assertEqual(4, line_product_1_id.product_uom_qty)
        line_product_2_id = lines.filtered(
            lambda l, product=self.product_2: l.product_id == product
        )
        self.assertEqual(2, line_product_2_id.product_uom_qty)
        self.assertEqual(so.applied_transaction_uuids, "uuid1,uuid2,uuid3,uuid4")

    def test_multi_transactions_multi_products_mix_create_update(self) -> None:
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        create_line_vals = self.env["sale.order.line"]._transactions_to_record_create(
            so, [CartTransaction(uuid="uuid1", product_id=self.product_1.id, qty=1)]
        )
        so.write({"order_line": [create_line_vals]})

        data = {
            "transactions": [
                {
                    "uuid": "uuid2",
                    "product_id": self.product_2.id,
                    "qty": 3,
                },
                {
                    "uuid": "uuid3",
                    "product_id": self.product_1.id,
                    "qty": 3,
                },
                {
                    "uuid": "uuid4",
                    "product_id": self.product_2.id,
                    "qty": -1,
                },
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            test_client.post(f"/sync/{so.uuid}", content=json.dumps(data))
        lines = so.order_line
        self.assertEqual(2, len(lines))
        line_product_1_id = lines.filtered(
            lambda l, product=self.product_1: l.product_id == product
        )
        self.assertEqual(4, line_product_1_id.product_uom_qty)
        line_product_2_id = lines.filtered(
            lambda l, product=self.product_2: l.product_id == product
        )
        self.assertEqual(2, line_product_2_id.product_uom_qty)
        self.assertEqual(so.applied_transaction_uuids, "uuid2,uuid3,uuid4")
