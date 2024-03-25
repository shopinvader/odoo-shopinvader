# Copyright 2024 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from fastapi import status
from requests import Response

from odoo.addons.shopinvader_api_cart.routers.cart import cart_router
from odoo.addons.shopinvader_api_cart.tests.common import CommonSaleCart


class TestSaleCart(CommonSaleCart):
    @classmethod
    def setUpClass(cls):
        super(TestSaleCart, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.address_step = cls.env.ref("sale_cart_step.cart_step_address")
        cls.checkout_step = cls.env.ref("sale_cart_step.cart_step_checkout")
        cls.last_step = cls.env.ref("sale_cart_step.cart_step_last")

    def test_update(self):
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        data = {
            "current_step": self.address_step.code,
            "next_step": self.checkout_step.code,
        }
        with self._create_test_client(router=cart_router) as test_client:
            response: Response = test_client.post(
                f"/{so.uuid}/update", content=json.dumps(data)
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.address_step, so.cart_step_done_ids)
        self.assertEqual(so.cart_step_id, self.checkout_step)
        data = response.json()
        self.assertEqual(
            data["step"], {"name": so.cart_step_id.name, "code": so.cart_step_id.code}
        )
        self.assertEqual(
            data["done_steps"],
            [{"name": x.name, "code": x.code} for x in so.cart_step_done_ids],
        )

        data = {
            "current_step": self.checkout_step.code,
            "next_step": self.last_step.code,
        }
        with self._create_test_client(router=cart_router) as test_client:
            response: Response = test_client.post(
                f"/{so.uuid}/update", content=json.dumps(data)
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.checkout_step, so.cart_step_done_ids)
        self.assertEqual(so.cart_step_id, self.last_step)
        data = response.json()
        self.assertEqual(
            data["step"], {"name": so.cart_step_id.name, "code": so.cart_step_id.code}
        )
        self.assertEqual(
            data["done_steps"],
            [{"name": x.name, "code": x.code} for x in so.cart_step_done_ids],
        )

    def test_get_no_step(self):
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        with self._create_test_client(router=cart_router) as test_client:
            response: Response = test_client.get(f"/{so.uuid}")

        data = response.json()
        self.assertEqual(data["step"], None)
        self.assertEqual(data["done_steps"], [])
