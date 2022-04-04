# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.sale_cart_rest_api.tests.common import TestSaleCartRestApiCase


class TestSaleCartDelivery(TestSaleCartRestApiCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleCartDelivery, cls).setUpClass()
        cls.poste_carrier = cls.env.ref("delivery.delivery_carrier")
        with cls.cart_service(
            authenticated_partner_id=cls.partner_1.id
        ) as cart:
            info = cart.sync(
                uuid=None,
                transactions=[
                    {
                        "uuid": "uuid1",
                        "product_id": cls.product_1.id,
                        "qty": 1,
                    }
                ],
            )
            cls.cart = cart
            cls.so = cls.env["sale.order"].browse(info["id"])

    def test_set_delivery_method(self):
        info = self.cart.dispatch(
            "set_delivery_method", params={"method_id": self.poste_carrier.id}
        )
        self.assertTrue(info)
        self.assertIn("method", info["delivery"])
        self.assertEqual(
            self.poste_carrier.id, info["delivery"]["method"]["id"]
        )
        self.assertIn("fees", info["delivery"])
        self.assertIn("amount_without_delivery", info)
