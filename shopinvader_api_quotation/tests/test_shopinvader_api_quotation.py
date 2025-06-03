# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from fastapi import status
from requests import Response

from odoo import Command
from odoo.exceptions import MissingError
from odoo.tests.common import tagged

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase

from ..routers import quotation_router


@tagged("post_install", "-at_install")
class TestQuotation(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        partner = cls.env["res.partner"].create({"name": "FastAPI Cart Demo"})

        cls.user_no_rights = cls.env["res.users"].create(
            {
                "name": "Test User Without Rights",
                "login": "user_no_rights",
                "groups_id": [Command.set([])],
            }
        )
        user_with_rights = cls.env["res.users"].create(
            {
                "name": "Test User With Rights",
                "login": "user_with_rights",
                "groups_id": [
                    (
                        Command.set(
                            [
                                cls.env.ref(
                                    "shopinvader_api_security_sale.shopinvader_sale_user_group"
                                ).id,
                            ]
                        )
                    )
                ],
            }
        )
        cls.default_fastapi_running_user = user_with_rights
        cls.default_fastapi_authenticated_partner = partner.with_user(user_with_rights)
        cls.default_fastapi_router = quotation_router

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

        cls.quotation = cls.env["sale.order"].create(
            {
                "partner_id": cls.default_fastapi_authenticated_partner.id,
                "quotation_state": "waiting_acceptation",
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product_1.id,
                            "product_uom_qty": 1.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product_2.id,
                            "product_uom_qty": 2.0,
                        }
                    ),
                ],
            }
        )

    def test_default_typology(self):
        self.assertEqual(self.quotation.typology, "quote")

    def test_search_quotations(self):
        # This one should not be returned as this is a "sale" and not a "quote"
        self.env["sale.order"].create(
            {
                "partner_id": self.default_fastapi_authenticated_partner.id,
                "quotation_state": "waiting_acceptation",
                "typology": "sale",
            }
        )
        with self._create_test_client() as test_client:
            response: Response = test_client.get("/quotations")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)

    def test_get_quotation(self):
        with self._create_test_client() as test_client:
            response: Response = test_client.get(f"/quotations/{self.quotation.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], self.quotation.name)

    def test_confirm_quotation(self):
        quotation = self.env["sale.order"].create(
            {
                "partner_id": self.default_fastapi_authenticated_partner.id,
                "quotation_state": "waiting_acceptation",
            }
        )
        with self._create_test_client() as test_client:
            response: Response = test_client.post(f"/quotations/{quotation.id}/confirm")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], quotation.id)

    def test_update_quotation(self):
        quotation = self.quotation
        data = {
            "client_order_ref": "PO_123123",
            "lines": [
                {
                    "line_id": quotation.order_line[0].id,
                    "sequence": 42,
                    "product_id": self.product_2.id,
                    "quantity": 123,
                },
                {
                    "sequence": 314,
                    "product_id": self.product_2.id,
                    "quantity": 200,
                },
                {
                    "product_id": self.product_1.id,
                    "quantity": 200,
                },
            ],
        }
        with self._create_test_client() as test_client:
            response: Response = test_client.post(
                f"/quotations/{quotation.id}", json=data
            )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )
        response_json = response.json()
        self.assertEqual(response_json["id"], quotation.id)
        self.assertEqual(quotation.client_order_ref, "PO_123123")
        self.assertEqual(quotation.order_line[0].product_id, self.product_2)
        self.assertEqual(quotation.order_line[0].product_uom_qty, 123)
        self.assertEqual(quotation.order_line[0].sequence, 42)
        self.assertEqual(len(quotation.order_line), 3)

    def test_create_quotation(self):
        data = {
            "name": "Test Quotation",
            "client_order_ref": "PO_12345",
            "lines": [
                {
                    "product_id": self.product_1.id,
                    "quantity": 1.0,
                },
                {
                    "product_id": self.product_2.id,
                    "quantity": 2.0,
                },
            ],
        }

        with self._create_test_client() as test_client:
            response: Response = test_client.post(
                "/quotations/create", content=json.dumps(data)
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response_json = response.json()
        self.assertIn("id", response_json)
        self.assertEqual(response_json["name"], "Test Quotation")
        self.assertEqual(response_json["typology"], "quote")
        self.assertEqual(response_json["client_order_ref"], "PO_12345")

        created_quotation = self.env["sale.order"].browse(response_json["id"])
        self.assertTrue(created_quotation.exists())
        self.assertEqual(created_quotation.name, "Test Quotation")
        self.assertEqual(
            created_quotation.partner_id.id,
            self.default_fastapi_authenticated_partner.id,
        )
        self.assertEqual(len(created_quotation.order_line), 2)
        self.assertEqual(
            created_quotation.order_line[0].product_id.id, self.product_1.id
        )
        self.assertEqual(created_quotation.order_line[0].product_uom_qty, 1.0)
        self.assertEqual(
            created_quotation.order_line[1].product_id.id, self.product_2.id
        )
        self.assertEqual(created_quotation.order_line[1].product_uom_qty, 2.0)

    def test_add_quotation_line(self):
        quotation = self.quotation

        data = {
            "product_id": self.product_1.id,
            "quantity": 3.0,
        }

        with self._create_test_client() as test_client:
            response: Response = test_client.post(
                f"/quotations/{quotation.id}/add_line", content=json.dumps(data)
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = response.json()
        self.assertEqual(response_json["id"], quotation.id)

        self.assertEqual(len(quotation.order_line), 3)
        self.assertEqual(quotation.order_line[-1].product_id.id, self.product_1.id)
        self.assertEqual(quotation.order_line[-1].product_uom_qty, 3.0)

    def test_add_quotation_lines(self):
        quotation = self.quotation

        data = {
            "lines": [
                {
                    "product_id": self.product_1.id,
                    "quantity": 3.0,
                },
                {
                    "product_id": self.product_2.id,
                    "quantity": 4.0,
                },
            ]
        }

        with self._create_test_client() as test_client:
            response: Response = test_client.post(
                f"/quotations/{quotation.id}/add_lines", content=json.dumps(data)
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_json = response.json()
        self.assertEqual(response_json["id"], quotation.id)

        self.assertEqual(len(quotation.order_line), 4)
        self.assertEqual(quotation.order_line[-2].product_id.id, self.product_1.id)
        self.assertEqual(quotation.order_line[-2].product_uom_qty, 3.0)
        self.assertEqual(quotation.order_line[-1].product_id.id, self.product_2.id)
        self.assertEqual(quotation.order_line[-1].product_uom_qty, 4.0)

    def test_update_quotation_line(self):
        quotation = self.quotation
        line_id = quotation.order_line[0].id
        data = {
            "line_id": line_id,
            "quantity": 42.0,
            "product_id": self.product_2.id,
            "sequence": 42,
        }

        with self._create_test_client() as test_client:
            response: Response = test_client.put(
                f"/quotations/{quotation.id}/update_line", content=json.dumps(data)
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertEqual(response_json["id"], quotation.id)

        self.assertEqual(len(quotation.order_line), 2)
        self.assertEqual(quotation.order_line[0].id, line_id)
        self.assertEqual(quotation.order_line[0].product_uom_qty, 42)
        self.assertEqual(quotation.order_line[0].product_id.id, self.product_2.id)
        self.assertEqual(quotation.order_line[0].sequence, 42)

        # test invalid line_id
        data["line_id"] = max(line.id for line in self.quotation.order_line) + 1
        with self._create_test_client() as test_client:
            with self.assertRaises(MissingError):
                response: Response = test_client.put(
                    f"/quotations/{quotation.id}/update_line", content=json.dumps(data)
                )

    def test_update_quotation_lines(self):
        quotation = self.quotation
        data = {
            "lines": [
                {
                    "line_id": quotation.order_line[0].id,
                    "quantity": 10,
                    "product_id": self.product_2.id,
                    "sequence": 10,
                },
                {
                    "line_id": quotation.order_line[1].id,
                    "quantity": 20,
                    "product_id": self.product_1.id,
                    "sequence": 20,
                },
            ]
        }

        with self._create_test_client() as test_client:
            response: Response = test_client.put(
                f"/quotations/{quotation.id}/update_lines", content=json.dumps(data)
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertEqual(response_json["id"], quotation.id)

        self.assertEqual(len(quotation.order_line), 2)

        self.assertEqual(quotation.order_line[0].id, data["lines"][0]["line_id"])
        self.assertEqual(quotation.order_line[0].product_uom_qty, 10)
        self.assertEqual(quotation.order_line[0].product_id.id, self.product_2.id)
        self.assertEqual(quotation.order_line[0].sequence, 10)

        self.assertEqual(quotation.order_line[1].id, data["lines"][1]["line_id"])
        self.assertEqual(quotation.order_line[1].product_uom_qty, 20)
        self.assertEqual(quotation.order_line[1].product_id.id, self.product_1.id)
        self.assertEqual(quotation.order_line[1].sequence, 20)

    def test_delete_quotation_line(self):
        quotation = self.quotation
        line_id = quotation.order_line[0].id
        data = {
            "line_id": line_id,
        }

        with self._create_test_client() as test_client:
            response: Response = test_client.post(
                f"/quotations/{quotation.id}/delete_line", content=json.dumps(data)
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertEqual(response_json["id"], quotation.id)

        self.assertEqual(len(quotation.order_line), 1)

        # test invalid line_id
        data["line_id"] = max(line.id for line in self.quotation.order_line) + 1
        with self._create_test_client() as test_client:
            with self.assertRaises(MissingError):
                response: Response = test_client.post(
                    f"/quotations/{quotation.id}/delete_line", content=json.dumps(data)
                )

    def test_delete_quotation_lines(self):
        quotation = self.quotation
        data = {
            "lines": [
                {
                    "line_id": quotation.order_line[0].id,
                },
                {
                    "line_id": quotation.order_line[1].id,
                },
            ]
        }

        with self._create_test_client() as test_client:
            response: Response = test_client.post(
                f"/quotations/{quotation.id}/delete_lines", content=json.dumps(data)
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertEqual(response_json["id"], quotation.id)

        self.assertEqual(len(quotation.order_line), 0)
