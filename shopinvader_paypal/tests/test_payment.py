# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase
from odoo.addons.shopinvader.services.cart import CartService
from odoo.addons.shopinvader.services.transaction import TransactionService

from odoo.addons.payment_gateway_paypal.tests.test_payment import (
    PaypalCommonCase,
    PaypalPaymentSuccess,
    paypal_mock)

from mock import Mock

REDIRECT_URL = {
    'redirect_cancel_url': 'https://IamGoingToKickYourAssIfYouDoNotPaid.com',
    'redirect_success_url': 'https://ThanksYou.com',
    }


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
        self.cart_service = self._get_service(CartService, self.partner)
        self.transaction_service = self._get_service(
            TransactionService, self.partner)
        self.cr.commit = Mock()  # TODO not commit

    def test_create_transaction(self):
        with paypal_mock(PaypalPaymentSuccess):
            params = REDIRECT_URL.copy()
            params['action'] = 'create'
            response = self.cart_service.update({
                'payment_method_id': self.payment_method.id,
                'payment_params': {'paypal': params}})
            self.assertEqual(response, {'redirect_to': 'https://redirect'})
            self._check_payment_create_sale_order({
                'cancel_url': REDIRECT_URL['redirect_cancel_url'],
                'return_url':
                    'http://locomotive.akretion/_store/check_transaction',
                })
            self.env['automatic.workflow.job'].run()
            self.assertEqual(self.sale.state, 'draft')

            transaction = self.sale.transaction_ids[0]
            response = self.transaction_service.get({
                'paymentId': transaction.external_id,
                })
            self.assertEqual(
                response['redirect_to'],
                REDIRECT_URL['redirect_success_url'])
            self.assertIn('store_cache', response)
            self.assertIn('last_sale', response['store_cache'])

            self.env['automatic.workflow.job'].run()
            self.assertNotEqual(self.sale.state, 'draft')
