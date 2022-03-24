# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from contextlib import contextmanager

import mock

from odoo.tests.common import SavepointCase

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.component.tests.common import ComponentMixin


class TestSaleCartRestApiCase(SavepointCase, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(TestSaleCartRestApiCase, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.setUpComponent()
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "product_1",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "product_2",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
            }
        )
        cls.partner_1 = cls.env["res.partner"].create({"name": "partner_1"})

        cls.partner_2 = cls.env["res.partner"].create({"name": "partner_2"})
        cls.public_partner = cls.env.ref("base.public_user").partner_id

        # create a cart for anonymous
        cls.anonymous_cart = cls._create_empty_cart()

    # pylint: disable=method-required-super
    def setUp(self):
        # resolve an inheritance issue (common.SavepointCase does not call
        # super)
        SavepointCase.setUp(self)
        ComponentMixin.setUp(self)

        # hack to be able to run tests if shopinvader is installed
        if "shopinvader.backend" in self.env:
            from odoo.addons.shopinvader import shopinvader_response

            shopinvader_response.set_testmode(True)
            shopinvader_response.get().reset()

            @self.addCleanup
            def cleanupShopinvaderResponseTestMode():
                shopinvader_response.set_testmode(False)

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
        ctx = dict(
            model_name="rest.service.registration",
            collection=collection,
            request=mock.Mock(),
            authenticated_partner_id=authenticated_partner_id,
        )
        # hack to be able to run tests if shopinvader is installed
        if "shopinvader.backend" in cls.env:
            ctx["shopinvader_backend"] = cls.env.ref("shopinvader.backend_1")
        work = WorkContext(**ctx)
        yield work.component(usage="cart")

    @classmethod
    def _create_empty_cart(cls, authenticated_partner_id=None):
        with cls.cart_service(
            authenticated_partner_id=authenticated_partner_id
        ) as cart:
            return cart._create_empty_cart()

    @contextmanager
    def assertEmptyResponse(self, cart):
        with mock.patch.object(cart.__class__, "request") as mocked_request:
            make_response = mock.MagicMock()
            mocked_request.make_response = make_response
            yield
            make_response.assert_called_once()
            make_response.assert_called_with(
                "{}", headers={"Content-Type": "application/json"}
            )
