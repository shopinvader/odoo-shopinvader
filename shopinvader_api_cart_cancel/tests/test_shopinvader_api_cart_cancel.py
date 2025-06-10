# Copyright 2025 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from fastapi import status
from requests import Response

from odoo.addons.shopinvader_api_cart.tests.common import CommonSaleCart

from ..routers.cart import cart_cancel_router


class TestSaleCart(CommonSaleCart):
    def test_cart_cancel(self) -> None:
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )

        with self._create_test_client(router=cart_cancel_router) as test_client:
            response: Response = test_client.post(f"/cancel/{so.uuid}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(so.state, "cancel")

        so2 = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        with self._create_test_client(router=cart_cancel_router) as test_client:
            response: Response = test_client.post("/cancel/current")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(so2.state, "cancel")
