# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import Depends, status

from odoo import api

from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.fastapi.routers import demo_router

from ..virtual_model import VirtualModel
from .common import CommonFastAPIEndpointCase, setup_models, unsetup_models


class RouterHelperTestContext(VirtualModel):
    _inherit = "shopinvader.router.helper"
    _name = "shopinvader.router.context_test.helper"

    def _get_endpoint_app(self):
        return f"{self.app}/{self.endpoint_id.name}"


def endpoint_helper(
    env: Annotated[api.Environment, Depends(odoo_env)],
):
    return env["shopinvader.router.context_test.helper"].new()


# Extend the demo router to have an endpoint that uses the helper and returns
# current app / endpoint
@demo_router.get("/demo/helper")
async def get_endpoint_app(
    helper: Annotated[RouterHelperTestContext, Depends(endpoint_helper)],
) -> str:
    """Returns the helper current app / endpoint"""
    return helper._get_endpoint_app()


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

    def setUp(self):
        super().setUp()
        setup_models(self.env, "shopinvader_router_helper")

    def tearDown(self):
        unsetup_models(self.env, "shopinvader_router_helper")
        super().tearDown()

    def test_context(self) -> None:
        with self._create_test_client(router=demo_router) as test_client:
            response = test_client.get("/demo/helper")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.text, '"demo/Fastapi Demo Endpoint"')
