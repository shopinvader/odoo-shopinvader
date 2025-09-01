# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from fastapi import status
from requests import Response

from odoo.tests.common import tagged

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase

from ..routers import sale_line_router, sale_router


@tagged("post_install", "-at_install")
class TestSale(FastAPITransactionCase):
    # TODO following code and access right must be shared between cart and sale
    # Maybe all the sale endpoint should be done in the shopinvader_api_cart ?
    # maybe we should named it "shopinvader_api_sale"
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        partner = cls.env["res.partner"].create({"name": "FastAPI Cart Demo"})

        cls.user_no_rights = cls.env["res.users"].create(
            {
                "name": "Test User Without Rights",
                "login": "user_no_rights",
                "groups_id": [(6, 0, [])],
            }
        )
        user_with_rights = cls.env["res.users"].create(
            {
                "name": "Test User With Rights",
                "login": "user_with_rights",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref(
                                "shopinvader_api_security_sale.shopinvader_sale_user_group"
                            ).id,
                        ],
                    )
                ],
            }
        )
        cls.default_fastapi_running_user = user_with_rights
        cls.default_fastapi_authenticated_partner = partner.with_user(user_with_rights)
        cls.default_fastapi_router = sale_router

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

        cls.so1 = cls.env["sale.order"].create(
            {"partner_id": cls.default_fastapi_authenticated_partner.id}
        )
        cls.so1.write(
            {
                "order_line": [
                    (0, 0, {"product_id": cls.product_1.id, "product_uom_qty": 2}),
                    (0, 0, {"product_id": cls.product_2.id, "product_uom_qty": 6}),
                ]
            }
        )
        cls.so2 = cls.env["sale.order"].create(
            {"partner_id": cls.default_fastapi_authenticated_partner.id}
        )
        cls.so2.write(
            {
                "order_line": [
                    (0, 0, {"product_id": cls.product_1.id, "product_uom_qty": 1}),
                    (0, 0, {"product_id": cls.product_2.id, "product_uom_qty": 3}),
                    (0, 0, {"product_id": cls.product_1.id, "product_uom_qty": 4}),
                ]
            }
        )

    def test_search_sales(self):
        with self._create_test_client() as test_client:
            response: Response = test_client.get("/sales")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 2)

    def test_get_sale(self):
        with self._create_test_client() as test_client:
            response: Response = test_client.get(f"/sales/{self.so1.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], self.so1.name)

    def test_download(self):
        with self._create_test_client() as test_client:
            response: Response = test_client.get(f"/sales/{self.so2.id}/download")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "application/pdf")

    def test_search_sale_lines(self):
        with self._create_test_client(router=sale_line_router) as test_client:
            response: Response = test_client.get("/sales/lines")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lines = response.json()
        self.assertEqual(lines["count"], 5)
        sols = lines["items"]
        self.assertEqual(sols[0]["order"]["id"], self.so2.id)
        self.assertEqual(sols[1]["order"]["id"], self.so2.id)
        self.assertEqual(sols[2]["order"]["id"], self.so2.id)
        self.assertEqual(sols[3]["order"]["id"], self.so1.id)
        self.assertEqual(sols[4]["order"]["id"], self.so1.id)
        self.assertEqual(sols[0]["order"]["name"], self.so2.name)
        self.assertEqual(sols[1]["order"]["name"], self.so2.name)
        self.assertEqual(sols[2]["order"]["name"], self.so2.name)
        self.assertEqual(sols[3]["order"]["name"], self.so1.name)
        self.assertEqual(sols[4]["order"]["name"], self.so1.name)
        self.assertEqual(sols[0]["order"]["state"], self.so2.state)
        self.assertEqual(sols[1]["order"]["state"], self.so2.state)
        self.assertEqual(sols[2]["order"]["state"], self.so2.state)
        self.assertEqual(sols[3]["order"]["state"], self.so1.state)
        self.assertEqual(sols[4]["order"]["state"], self.so1.state)
        self.assertEqual(
            sols[0]["order"]["date_order"],
            self.so2.date_order.isoformat(timespec="seconds"),
        )
        self.assertEqual(
            sols[1]["order"]["date_order"],
            self.so2.date_order.isoformat(timespec="seconds"),
        )
        self.assertEqual(
            sols[2]["order"]["date_order"],
            self.so2.date_order.isoformat(timespec="seconds"),
        )
        self.assertEqual(
            sols[3]["order"]["date_order"],
            self.so1.date_order.isoformat(timespec="seconds"),
        )
        self.assertEqual(
            sols[4]["order"]["date_order"],
            self.so1.date_order.isoformat(timespec="seconds"),
        )

    def test_search_sale_lines_by_sale(self):
        with self._create_test_client(router=sale_line_router) as test_client:
            response: Response = test_client.get(f"/sales/{self.so2.id}/lines")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lines = response.json()
        self.assertEqual(lines["count"], 3)
        sols = lines["items"]
        self.assertEqual(sols[0]["order"]["id"], self.so2.id)
        self.assertEqual(sols[1]["order"]["id"], self.so2.id)
        self.assertEqual(sols[2]["order"]["id"], self.so2.id)
        self.assertEqual(sols[0]["order"]["name"], self.so2.name)
        self.assertEqual(sols[1]["order"]["name"], self.so2.name)
        self.assertEqual(sols[2]["order"]["name"], self.so2.name)
        self.assertEqual(sols[0]["order"]["state"], self.so2.state)
        self.assertEqual(sols[1]["order"]["state"], self.so2.state)
        self.assertEqual(sols[2]["order"]["state"], self.so2.state)

    def test_search_sale_lines_by_name(self):
        with self._create_test_client(router=sale_line_router) as test_client:
            response: Response = test_client.get(
                "/sales/lines", params={"order_name": self.so2.name}
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lines = response.json()
        self.assertEqual(lines["count"], 3)
        sols = lines["items"]
        self.assertEqual(sols[0]["order"]["id"], self.so2.id)
        self.assertEqual(sols[1]["order"]["id"], self.so2.id)
        self.assertEqual(sols[2]["order"]["id"], self.so2.id)
        self.assertEqual(sols[0]["order"]["name"], self.so2.name)
        self.assertEqual(sols[1]["order"]["name"], self.so2.name)
        self.assertEqual(sols[2]["order"]["name"], self.so2.name)
        self.assertEqual(sols[0]["order"]["state"], self.so2.state)
        self.assertEqual(sols[1]["order"]["state"], self.so2.state)
        self.assertEqual(sols[2]["order"]["state"], self.so2.state)

    def test_search_sale_lines_by_product_name(self):
        with self._create_test_client(router=sale_line_router) as test_client:
            response: Response = test_client.get(
                "/sales/lines", params={"product_name": self.product_2.name}
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lines = response.json()
        self.assertEqual(lines["count"], 2)
        sols = lines["items"]
        self.assertEqual(sols[0]["order"]["id"], self.so2.id)
        self.assertEqual(sols[1]["order"]["id"], self.so1.id)
        self.assertEqual(sols[0]["order"]["name"], self.so2.name)
        self.assertEqual(sols[1]["order"]["name"], self.so1.name)
        self.assertEqual(sols[0]["order"]["state"], self.so2.state)
        self.assertEqual(sols[1]["order"]["state"], self.so1.state)

    def test_get_sale_line(self):
        with self._create_test_client(router=sale_line_router) as test_client:
            response: Response = test_client.get(
                f"/sales/lines/{self.so2.order_line[0].id}"
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sol = response.json()
        self.assertEqual(sol["order"]["id"], self.so2.id)
        self.assertEqual(sol["order"]["name"], self.so2.name)
        self.assertEqual(sol["order"]["state"], self.so2.state)
