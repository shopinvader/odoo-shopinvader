# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from contextlib import contextmanager
from unittest import mock

from fastapi import status
from requests import Response

from odoo.tests.common import tagged

from odoo.addons.shopinvader_api_cart.tests.common import CommonSaleCart
from odoo.addons.shopinvader_api_sale.routers import sale_line_router
from odoo.addons.shopinvader_unit_management.tests.common import (
    TestUnitManagementCommon,
)

from ..routers import cart_router, unit_request_line_router


@tagged("post_install", "-at_install")
class TestShopinvaderUnitCartApi(TestUnitManagementCommon, CommonSaleCart):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref(
                                "shopinvader_api_unit_member."
                                "shopinvader_unit_management_user_group"
                            ).id
                        ],
                    )
                ],
            }
        )

        cls.default_fastapi_authenticated_partner = cls.collaborator_1_1.with_user(
            cls.default_fastapi_running_user
        )
        cls.default_fastapi_router = sale_line_router
        cls.sale_line_app = cls.env.ref("fastapi.fastapi_endpoint_demo")._get_app()
        cls.default_fastapi_router = cart_router
        cls.default_fastapi_app = cls.cart_app = cls.env.ref(
            "fastapi.fastapi_endpoint_demo"
        )._get_app()

        cls.cart_1_1_pending = cls.env["sale.order"]._create_empty_cart(
            cls.collaborator_1_1.id
        )
        cls.cart_1_1_pending.write(
            {
                "order_line": [
                    (0, 0, {"product_id": cls.product_1.id, "product_uom_qty": 8}),
                ]
            }
        )
        cls.cart_1_1 = cls.env["sale.order"]._create_empty_cart(cls.collaborator_1_1.id)
        cls.cart_1_1.write(
            {
                "order_line": [
                    (0, 0, {"product_id": cls.product_1.id, "product_uom_qty": 2}),
                    (0, 0, {"product_id": cls.product_2.id, "product_uom_qty": 6}),
                ]
            }
        )
        cls.cart_1_1.action_request_cart()

        cls.cart_1_2 = cls.env["sale.order"]._create_empty_cart(cls.collaborator_1_2.id)
        cls.cart_1_2.write(
            {
                "order_line": [
                    (0, 0, {"product_id": cls.product_1.id, "product_uom_qty": 3}),
                ]
            }
        )
        cls.cart_1_2.action_request_cart()
        cls.cart_3_2 = cls.env["sale.order"]._create_empty_cart(cls.collaborator_3_2.id)
        cls.cart_3_2.write(
            {
                "order_line": [
                    (0, 0, {"product_id": cls.product_2.id, "product_uom_qty": 4}),
                ]
            }
        )
        cls.cart_3_2.action_request_cart()
        cls.cart_1_1_manager = cls.env["sale.order"]._create_empty_cart(
            cls.manager_1_1.id
        )
        cls.cart_1_1_manager.write(
            {
                "order_line": [
                    (0, 0, {"product_id": cls.product_1.id, "product_uom_qty": 12}),
                    (0, 0, {"product_id": cls.product_2.id, "product_uom_qty": 5}),
                ]
            }
        )

    def _slice_sol(self, data, *fields):
        if len(fields) == 1:
            return {item[fields[0]] for item in data["items"]}
        return {tuple(item[field] for field in fields) for item in data["items"]}

    @contextmanager
    def _rollback_called_test_client(self, **kwargs):
        with self._create_test_client(**kwargs) as test_client, mock.patch.object(
            self.env.cr.__class__, "rollback"
        ) as mock_rollback:
            yield test_client
            mock_rollback.assert_called_once()

    def test_cart_request_as_collaborator(self):
        """
        Test to request a cart as a collaborator
        """
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        self.assertEqual(so.state, "draft")
        self.assertEqual(so.typology, "cart")

        with self._create_test_client() as test_client:
            response: Response = test_client.get(f"/{so.uuid}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        info = response.json()
        self.assertEqual(info["id"], so.id)

        with self._create_test_client() as test_client:
            response: Response = test_client.post(
                "/request",
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        self.assertEqual(so.typology, "request")

    def test_cart_request_as_collaborator_uuid(self):
        """
        Test to request a cart as a collaborator
        """
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        self.assertEqual(so.state, "draft")
        self.assertEqual(so.typology, "cart")

        with self._create_test_client() as test_client:
            response: Response = test_client.get(f"/{so.uuid}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        info = response.json()
        self.assertEqual(info["id"], so.id)

        with self._create_test_client() as test_client:
            response: Response = test_client.post(
                f"/{so.uuid}/request",
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        self.assertEqual(so.typology, "request")

    def test_cart_request_as_manager(self):
        """
        Test to request a cart as a manager
        """
        self.default_fastapi_authenticated_partner = self.manager_1_1.with_user(
            self.default_fastapi_running_user
        )

        self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        with self._rollback_called_test_client() as test_client:
            response: Response = test_client.post("/request")
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
            )

    def test_cart_request_as_unit(self):
        """
        Test to request a cart as a unit
        """
        self.default_fastapi_authenticated_partner = self.unit_1.with_user(
            self.default_fastapi_running_user
        )

        self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        with self._rollback_called_test_client() as test_client:
            response: Response = test_client.post("/request")
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
            )

    def test_cart_request_saved_quantities(self):
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        self.assertEqual(so.state, "draft")
        self.assertEqual(so.typology, "cart")

        # Add a product to the cart
        so.write(
            {
                "order_line": [
                    (0, 0, {"product_id": self.product_1.id, "product_uom_qty": 2}),
                    (0, 0, {"product_id": self.product_2.id, "product_uom_qty": 6}),
                ]
            }
        )

        self.assertEqual(so.order_line[0].product_uom_qty, 2)
        self.assertEqual(so.order_line[1].product_uom_qty, 6)
        self.assertEqual(so.order_line[0].qty_requested, 0)
        self.assertEqual(so.order_line[1].qty_requested, 0)

        with self._create_test_client() as test_client:
            response: Response = test_client.post(
                "/request",
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        self.assertEqual(so.typology, "request")
        self.assertEqual(so.order_line[0].product_uom_qty, 2)
        self.assertEqual(so.order_line[1].product_uom_qty, 6)
        self.assertEqual(so.order_line[0].qty_requested, 2)
        self.assertEqual(so.order_line[1].qty_requested, 6)

    def test_sale_line_requested_flow(self):
        so = self.env["sale.order"]._create_empty_cart(self.manager_2_1.id)
        so1 = self.env["sale.order"]._create_empty_cart(self.collaborator_2_1.id)
        so1.write(
            {
                "order_line": [
                    (0, 0, {"product_id": self.product_1.id, "product_uom_qty": 2}),
                    (0, 0, {"product_id": self.product_2.id, "product_uom_qty": 6}),
                ]
            }
        )
        so1.action_confirm_cart()
        so2 = self.env["sale.order"]._create_empty_cart(self.collaborator_2_1.id)
        so2.write(
            {
                "order_line": [
                    (0, 0, {"product_id": self.product_1.id, "product_uom_qty": 1}),
                    (0, 0, {"product_id": self.product_2.id, "product_uom_qty": 3}),
                    (0, 0, {"product_id": self.product_1.id, "product_uom_qty": 4}),
                ]
            }
        )

        with self._create_test_client(partner=self.collaborator_2_1) as test_client:
            response: Response = test_client.post(f"/{so2.uuid}/request")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        self.assertEqual(so1.typology, "sale")
        self.assertEqual(so2.typology, "request")

        with self._create_test_client(
            app=self.sale_line_app,
            router=sale_line_router,
            partner=self.collaborator_2_1,
        ) as test_client:
            response: Response = test_client.get("/sale_lines")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        self.assertEqual(response.json()["count"], 5)

        with self._create_test_client(
            app=self.sale_line_app,
            router=unit_request_line_router,
            partner=self.manager_2_1,
        ) as test_client:
            response: Response = test_client.get("/unit/request_lines")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        self.assertEqual(response.json()["count"], 3)

        so2.order_line[:2]._action_accept_request(so)

        with self._create_test_client(
            app=self.sale_line_app,
            router=sale_line_router,
            partner=self.collaborator_2_1,
        ) as test_client:
            response: Response = test_client.get("/sale_lines")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        self.assertEqual(response.json()["count"], 5)

        with self._create_test_client(
            app=self.sale_line_app,
            router=unit_request_line_router,
            partner=self.manager_2_1,
        ) as test_client:
            response: Response = test_client.get("/unit/request_lines")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        self.assertEqual(response.json()["count"], 1)

    def test_sale_line_requested_as_collaborator(self):
        with self._rollback_called_test_client(
            app=self.sale_line_app, router=unit_request_line_router
        ) as test_client:
            response: Response = test_client.get("/unit/request_lines")
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
            )

    def test_sale_line_requested_filters(self):
        with self._create_test_client(
            app=self.sale_line_app,
            router=unit_request_line_router,
            partner=self.manager_1_1,
        ) as test_client:
            response: Response = test_client.get("/unit/request_lines")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertEqual(res["count"], 3)
        self.assertEqual(
            self._slice_sol(res, "product_id", "qty", "order_id"),
            {
                (self.product_1.id, 2, self.cart_1_1.id),
                (self.product_2.id, 6, self.cart_1_1.id),
                (self.product_1.id, 3, self.cart_1_2.id),
            },
        )

    def test_sale_line_requested_accept(self):
        so = self.env["sale.order"]._create_empty_cart(self.manager_1_1.id)

        sol = self.cart_1_1.order_line.filtered(
            lambda p: p.product_id == self.product_1
        )
        self.assertEqual(sol.qty_requested, 2)
        self.assertEqual(sol.request_partner_id, self.collaborator_1_1)
        self.assertFalse(sol.request_order_id)

        with self._create_test_client(
            app=self.sale_line_app,
            router=unit_request_line_router,
            partner=self.manager_1_1,
        ) as test_client:
            response: Response = test_client.post(
                f"/unit/request_lines/{sol.id}/accept"
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        self.assertEqual(sol.qty_requested, 2)
        self.assertEqual(sol.request_partner_id, self.collaborator_1_1)
        self.assertEqual(sol.order_id, so)
        self.assertEqual(sol.request_order_id, self.cart_1_1)
        self.assertFalse(sol.reject_order_id)
        self.assertEqual(len(so.order_line), 1)

        with self._create_test_client(
            app=self.sale_line_app,
            router=unit_request_line_router,
            partner=self.manager_1_1,
        ) as test_client:
            response: Response = test_client.get("/unit/request_lines")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertEqual(res["count"], 2)
        self.assertEqual(
            self._slice_sol(res, "product_id", "qty", "order_id"),
            {
                (self.product_2.id, 6, self.cart_1_1.id),
                (self.product_1.id, 3, self.cart_1_2.id),
            },
        )

        with self._create_test_client(partner=self.manager_1_1) as test_client:
            response: Response = test_client.get(f"/{so.uuid}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.json()
        self.assertEqual(res["id"], so.id)
        self.assertEqual(len(res["lines"]), 1)
        self.assertEqual(res["lines"][0]["product_id"], self.product_1.id)
        self.assertEqual(res["lines"][0]["qty"], 2)

    def test_sale_line_requested_reject(self):
        so = self.env["sale.order"]._create_empty_cart(self.manager_1_1.id)
        sol = self.cart_1_1.order_line.filtered(
            lambda p: p.product_id == self.product_1
        )
        self.assertEqual(sol.qty_requested, 2)
        self.assertEqual(sol.request_partner_id, self.collaborator_1_1)
        self.assertFalse(sol.request_order_id)

        with self._create_test_client(
            app=self.sale_line_app,
            router=unit_request_line_router,
            partner=self.manager_1_1,
        ) as test_client:
            response: Response = test_client.post(
                f"/unit/request_lines/{sol.id}/reject",
                data=json.dumps({"reason": "Don't Want"}),
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        self.assertEqual(sol.qty_requested, 2)
        self.assertEqual(sol.request_partner_id, self.collaborator_1_1)
        self.assertEqual(sol.order_id, self.cart_1_1)
        self.assertFalse(sol.request_order_id)
        self.assertEqual(sol.reject_order_id, so)
        self.assertTrue(sol.request_rejected)
        self.assertEqual(sol.request_rejection_reason, "Don't Want")

        with self._create_test_client(
            app=self.sale_line_app,
            router=unit_request_line_router,
            partner=self.manager_1_1,
        ) as test_client:
            response: Response = test_client.get("/unit/request_lines")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertEqual(res["count"], 2)
        self.assertEqual(
            self._slice_sol(res, "product_id", "qty", "order_id"),
            {
                (self.product_2.id, 6, self.cart_1_1.id),
                (self.product_1.id, 3, self.cart_1_2.id),
            },
        )

        with self._create_test_client(
            app=self.sale_line_app,
            router=unit_request_line_router,
            partner=self.manager_1_1,
        ) as test_client:
            response: Response = test_client.get(
                "/unit/request_lines", params={"rejected": True}
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertEqual(res["count"], 3)
        self.assertEqual(
            self._slice_sol(
                res,
                "product_id",
                "qty",
                "order_id",
                "request_rejected",
                "request_rejection_reason",
            ),
            {
                (self.product_1.id, 2, self.cart_1_1.id, True, "Don't Want"),
                (self.product_2.id, 6, self.cart_1_1.id, False, None),
                (self.product_1.id, 3, self.cart_1_2.id, False, None),
            },
        )

    def test_sale_line_requested_reset(self):
        so = self.env["sale.order"]._create_empty_cart(self.manager_1_1.id)
        sol = self.cart_1_1.order_line.filtered(
            lambda p: p.product_id == self.product_1
        )
        sol._action_reject_request(so, "Don't Want")
        self.assertTrue(sol.request_rejected)
        self.assertEqual(sol.request_rejection_reason, "Don't Want")

        with self._create_test_client(
            app=self.sale_line_app,
            router=unit_request_line_router,
            partner=self.manager_1_1,
        ) as test_client:
            response: Response = test_client.post(
                f"/unit/request_lines/{sol.id}/reset",
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        self.assertFalse(sol.request_rejected)
        self.assertFalse(sol.request_rejection_reason)

    def test_sale_line_unlink_accepted(self):
        so = self.env["sale.order"]._create_empty_cart(self.manager_1_1.id)
        sol = self.cart_1_1.order_line.filtered(
            lambda p: p.product_id == self.product_1
        )

        sol._action_accept_request(so)
        sol.product_uom_qty = 1

        self.assertEqual(sol.order_id, so)
        self.assertEqual(sol.request_order_id, self.cart_1_1)
        self.assertEqual(sol.request_partner_id, self.collaborator_1_1)
        self.assertEqual(sol.product_uom_qty, 1)
        self.assertEqual(sol.qty_requested, 2)

        sol.unlink()

        self.assertEqual(sol.order_id, self.cart_1_1)
        self.assertFalse(sol.request_order_id)
        self.assertEqual(sol.request_partner_id, self.collaborator_1_1)
        self.assertEqual(sol.product_uom_qty, 2)
        self.assertEqual(sol.qty_requested, 2)

    def test_cart_confirm_notify_collaborators(self):
        so = self.env["sale.order"]._create_empty_cart(self.manager_1_1.id)
        sol = self.cart_1_1.order_line.filtered(
            lambda p: p.product_id == self.product_1
        )
        sol2 = self.cart_1_1.order_line.filtered(
            lambda p: p.product_id == self.product_2
        )
        sol._action_accept_request(so)
        sol2._action_reject_request(so, "Nope")
        self.cart_1_2.order_line._action_accept_request(so)
        self.assertEqual(len(self.collaborator_1_1.message_ids), 0)
        self.assertEqual(len(self.collaborator_1_2.message_ids), 0)

        so.action_confirm()

        # Check that the partners have been notified
        self.assertEqual(len(self.collaborator_1_1.message_ids), 1)
        self.assertEqual(len(self.collaborator_1_2.message_ids), 1)
        message = self.collaborator_1_1.message_ids[0]
        self.assertIn("Your following requests have been accepted:", message.body)
        self.assertIn("product_1 - 2.0", message.body)
        self.assertIn("Your following requests have been rejected:", message.body)
        self.assertIn("product_2 - 6.0: Nope", message.body)
        message = self.collaborator_1_2.message_ids[0]
        self.assertIn("Your following requests have been accepted:", message.body)
        self.assertIn("product_1 - 3.0", message.body)
        self.assertEqual(len(self.manager_1_1.message_ids), 0)
