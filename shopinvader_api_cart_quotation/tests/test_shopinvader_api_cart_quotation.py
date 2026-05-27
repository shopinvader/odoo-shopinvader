# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from fastapi import status
from requests import Response

from odoo import Command
from odoo.tests.common import tagged

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase

from ..routers import cart_quotation_router


@tagged("post_install", "-at_install")
class TestCartQuotation(FastAPITransactionCase):
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
        cls.default_fastapi_router = cart_quotation_router

    def test_request_quotation(self):
        cart = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        with self._create_test_client() as test_client:
            response: Response = test_client.post(f"/{cart.uuid}/request_quotation")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertEqual(response_json["uuid"], cart.uuid)
        self.assertEqual(response_json["typology"], "sale")
