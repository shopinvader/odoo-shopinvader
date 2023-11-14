# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from fastapi import status
from requests import Response

from odoo.tests.common import tagged

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase

from ..routers.quotation import quotation_router


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
                                "shopinvader_api_cart.shopinvader_cart_user_group"
                            ).id,
                        ],
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

    def test_search_quotations(self):
        self.env["sale.order"].create(
            {
                "partner_id": self.default_fastapi_authenticated_partner.id,
                "typology": "quotation",
            }
        )
        with self._create_test_client(router=quotation_router) as test_client:
            response: Response = test_client.get("/quotations")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)

    def test_get_quotation(self):
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.default_fastapi_authenticated_partner.id,
                "typology": "quotation",
            }
        )
        with self._create_test_client(router=quotation_router) as test_client:
            response: Response = test_client.get(f"/quotations/{sale.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], sale.name)

    def test_confirm_quotation(self):
        quotation = self.env["sale.order"].create(
            {
                "partner_id": self.default_fastapi_authenticated_partner.id,
                "typology": "quotation",
            }
        )
        with self._create_test_client(router=quotation_router) as test_client:
            response: Response = test_client.get(f"/quotations/{quotation.id}/confirm")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], quotation.id)
