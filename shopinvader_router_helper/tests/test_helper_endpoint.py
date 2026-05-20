# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from fastapi import status

from odoo.addons.fastapi.routers import demo_router

from .common import CommonFastAPIEndpointCase


class EndpointRouterContextCase(CommonFastAPIEndpointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env.ref("fastapi.my_demo_app_user")
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "testpartner@example.com",
            }
        )
        cls.endpoint = cls.env.ref("fastapi.fastapi_endpoint_demo")

        cls.setUpEndpoint(cls.endpoint, cls.user, cls.partner)

    def test_context(self) -> None:
        with self._create_test_client(router=demo_router) as test_client:
            response = test_client.get("/demo/helper")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.text, '"demo/Fastapi Demo Endpoint"')
