# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase
from odoo.addons.payment_gateway_adyen.tests.test_payment import (
    AdyenCommonCase,
    AdyenScenario)
import json
from mock import Mock
from os.path import dirname


REDIRECT_URL = {
    'redirect_cancel_url': 'https://IamGoingToKickYourAssIfYouDoNotPaid.com',
    'redirect_success_url': 'https://ThanksYou.com',
    }


class ShopinvaderAdyenCase(AdyenCommonCase, CommonCase, AdyenScenario):

    def __init__(self, *args, **kwargs):
        super(ShopinvaderAdyenCase, self).__init__(*args, **kwargs)
        self._decorate_test(dirname(__file__))

    def setUp(self, *args, **kwargs):
        super(ShopinvaderAdyenCase, self).setUp(*args, **kwargs)
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
        with self.work_on_services(
                partner=self.partner,
                shopinvader_session=self.shopinvader_session) as work:
            self.service = work.component(usage='cart')
        self.cr.commit = Mock()  # Do not commit

    def _create_transaction(self, card):
        params = REDIRECT_URL.copy()
        params['encrypted_card'] = self._get_encrypted_card(card)
        response = self.service.dispatch('add_payment', params={
            'payment_mode': {'id': self.account_payment_mode.id},
            'adyen': params})
        transaction = self.sale.transaction_ids
        self.assertEqual(len(transaction), 1)
        self.assertEqual(
            self.sale.workflow_process_id,
            self.account_payment_mode.workflow_process_id)
        return response, transaction, json.loads(transaction.data)

    def _check_captured(self, transaction, response,
                        expected_state='succeeded',
                        expected_risk_level='normal'):
        self.assertEqual(transaction.state, expected_state)
        data = json.loads(transaction.data)
        self.assertEqual(self.sale.amount_total, transaction.amount)
        self.assertEqual(data['response'], u'[capture-received]')

        self.assertIn('store_cache', response)
        self.assertIn('last_sale', response['store_cache'])

    def _test_3d(self, card, success=True):
        response, transaction, source = self._create_transaction(card)
        self.assertEqual(response['redirect_to'], transaction.url)
        self.assertEqual(transaction.state, 'pending')

        self._fill_3d_secure(transaction, card, success=success)
        response = self.service.dispatch('check_payment', params={
            'source': source['id'],
            'provider_name': 'adyen',
            })
        if success:
            self._check_captured(transaction, response)
            self.assertEqual(
                response['redirect_to'],
                REDIRECT_URL['redirect_success_url'])
        else:
            self.assertEqual(transaction.state, 'failed')
            self.assertEqual(
                response['redirect_to'],
                REDIRECT_URL['redirect_cancel_url'])
            self.assertIn('store_cache', response)
            self.assertIn('notifications', response['store_cache'])

    def _test_card(self, card, **kwargs):
        response, transaction, source = self._create_transaction(card)
        self._check_captured(transaction, response, **kwargs)
        self.assertNotIn('redirect_to', response)

#    def test_create_transaction_3d_not_supported(self):
#        response, transaction, source =\
#            self._create_transaction('378282246310005')
#        self._check_captured(transaction, response)
#        self.assertNotIn('redirect_to', response)
