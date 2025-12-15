# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from unittest import skipIf

from fastapi import status
from requests import Response

try:
    from odoo.addons.shopinvader_api_cart.routers import cart_router
    from odoo.addons.shopinvader_api_cart.tests.common import CommonSaleCart
except ImportError:
    cart_router = None
    CommonSaleCart = object


@skipIf(cart_router is None, "shopinvader_api_cart not installed")
class TestShopinvaderSaleChannelCart(CommonSaleCart):
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

        cls.endpoint = cls.env.ref("fastapi.fastapi_endpoint_demo")
        cls.endpoint.sale_channel_id = cls.sale_channel.id

        # We use the api_key auth method here to be able to authenticate as
        # a partner with the real dependency machinery (env creation)
        cls.endpoint.demo_auth_method = "api_key"

        cls.default_fastapi_app = cls.endpoint._get_app()
        cls.default_fastapi_dependency_overrides = (
            cls.default_fastapi_app.dependency_overrides
        )
        cls.default_fastapi_authenticated_partner = False

    def test_sale_channel_in_cart(self):
        # Clear carts
        self.env["sale.order"].search(
            [("typology", "=", "cart"), ("state", "=", "draft")]
        ).unlink()
        # Create a cart
        data = {
            "transactions": [
                {
                    "uuid": self.trans_uuid_1,
                    "product_id": self.product_1.id,
                    "qty": 1,
                }
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            response: Response = test_client.post(
                "/current/sync",
                content=json.dumps(data),
                headers={"api-key": "user_with_rights"},
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        so = self.env["sale.order"].search(
            [
                ("partner_id", "=", self.default_fastapi_running_user.partner_id.id),
                ("typology", "=", "cart"),
                ("state", "=", "draft"),
            ],
            limit=1,
        )
        self.assertEqual(so.sale_channel_id, self.sale_channel)
