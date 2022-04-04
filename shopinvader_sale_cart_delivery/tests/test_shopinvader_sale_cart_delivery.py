# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from contextlib import contextmanager

import mock

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.shopinvader.tests.common import CommonCase


class TestShopinvaderSaleCartDelivery(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestShopinvaderSaleCartDelivery, cls).setUpClass()
        cls.product_1 = cls.env.ref("product.product_product_4b")
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.poste_carrier = cls.env.ref("delivery.delivery_carrier")

        with cls.cart_service(authenticated_partner_id=cls.partner.id) as cart:
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
            cls.so = cls.env["sale.order"].browse(info["id"])
            cls.cart_service = cart

    @classmethod
    @contextmanager
    def cart_service(cls, authenticated_partner_id):
        env = cls.env(
            context=dict(
                cls.env.context,
                authenticated_partner_id=authenticated_partner_id,
            )
        )
        collection = _PseudoCollection("shopinvader.api.v2", env)
        work = WorkContext(
            model_name="rest.service.registration",
            collection=collection,
            request=mock.Mock(),
            authenticated_partner_id=authenticated_partner_id,
            shopinvader_backend=cls.backend,
        )
        yield work.component(usage="cart")

    def test_set_carrier(self):
        info = self.cart_service.dispatch(
            "set_delivery_method", params={"method_id": self.poste_carrier.id}
        )
        self.assertTrue(info)
        self.assertIn("delivery", info)
