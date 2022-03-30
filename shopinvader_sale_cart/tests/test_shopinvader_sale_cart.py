# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from contextlib import contextmanager

import mock

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.shopinvader.tests.common import CommonCase


class TestShopinvaderSaleCart(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestShopinvaderSaleCart, cls).setUpClass()
        cls.product_1 = cls.env.ref("product.product_product_4b")

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

    @classmethod
    def _create_empty_cart(cls, authenticated_partner_id=None):
        with cls.cart_service(
            authenticated_partner_id=authenticated_partner_id
        ) as cart:
            return cart._create_empty_cart()

    def test_shopinvader_cart_backend_info(self):
        with self.cart_service(None) as cart:
            info = cart.sync(
                uuid=None,
                transactions=[
                    {
                        "uuid": "uuid1",
                        "product_id": self.product_1.id,
                        "qty": 1,
                    }
                ],
            )
            self.assertTrue(info)
            so = self.env["sale.order"].browse(info["id"])
            self.assertEqual(so.partner_id, self.backend.anonymous_partner_id)
            self.assertEqual(so.pricelist_id, self.backend.pricelist_id)
            self.assertEqual(so.shopinvader_backend_id, self.backend)
            self.assertEqual(info["state"], so.shopinvader_state)
            self.assertEqual(
                info["state_label"],
                cart._get_selection_label(so, "shopinvader_state"),
            )
