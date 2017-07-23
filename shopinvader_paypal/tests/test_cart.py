# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.shopinvader.tests.common import CommonCase
from openerp.addons.shopinvader.services.cart import CartService

from openerp.addons.payment_gateway_paypal.tests.test_payment import (
    PaypalCommonCase,
    PaypalPaymentSuccess,
    REDIRECT_URL,
    paypal_mock)


class ShopinvaderPaypalCase(PaypalCommonCase, CommonCase):

    def setUp(self, *args, **kwargs):
        super(ShopinvaderPaypalCase, self).setUp(*args, **kwargs)
        self.shopinvader_session = {'cart_id': self.sale.id}
        self.partner = self.sale.partner_id
        self.env['shopinvader.partner'].create({
            'record_id': self.partner.id,
            'external_id': 'ZG9kbw==',
            'backend_id': self.backend.id,
            })
        self.sale.write({
            'typology': 'cart',
            'shopinvader_backend_id': self.backend.id,
            })
        self.service = self._get_service(CartService, self.partner)

    def test_create_transaction(self):
        with paypal_mock(PaypalPaymentSuccess):
            params = REDIRECT_URL.copy()
            params['action'] = 'create'
            response = self.service.update(
                {'payment_params': {'paypal': params}})
            self.assertEqual(response, {'redirect_to': 'https://redirect'})
            self._check_payment_create_sale_order()
