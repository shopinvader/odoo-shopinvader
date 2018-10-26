# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.addons.shopinvader.tests.common import CommonCase
from odoo.addons.payment_gateway_adyen.tests.test_payment import (
    AdyenCommonCase,
    AdyenScenario,
    SHOPPER_IP,
    ACCEPT_HEADER,
    USER_AGENT)
from odoo.addons.payment_gateway.tests.common import PaymentScenarioType
import json
from mock import Mock
from os.path import dirname


REDIRECT_URL = {
    'redirect_cancel_url': 'https://IamGoingToKickYourAssIfYouDoNotPaid.com',
    'redirect_success_url': 'https://ThanksYou.com',
    }


class ShopinvaderAdyenCommonCase(AdyenCommonCase, CommonCase):

    def setUp(self, *args, **kwargs):
        super(ShopinvaderAdyenCommonCase, self).setUp(*args, **kwargs)
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

    def _prepare_transaction_params(self, card):
        params = REDIRECT_URL.copy()
        params.update({
            'token': self._get_encrypted_card(card),
            'accept_header': ACCEPT_HEADER,
            'user_agent': USER_AGENT,
            'shopper_ip': SHOPPER_IP,
            })
        return params

    def _create_transaction(self, card):
        params = self._prepare_transaction_params(card)
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

    def _get_data_for_3d_secure(self, response):
        data = response['data']['payment']['adyen_params']
        url = data.pop('IssuerUrl')
        return url, data

    def _prepare_transaction_return_params(self, transaction, pares):
        return {
            'md': transaction.meta['MD'],
            'pares': pares,
            'provider_name': 'adyen',
            'accept_header': ACCEPT_HEADER,
            'user_agent': USER_AGENT,
            'shopper_ip': SHOPPER_IP,
            }

    def _test_3d(self, card, success=True):
        response, transaction, source = self._create_transaction(card)
        self.assertEqual(transaction.state, 'pending')
        url, data = self._get_data_for_3d_secure(response)
        pares = self._fill_3d_secure(transaction, card, success=success)
        params = self._prepare_transaction_return_params(transaction, pares)
        if success:
            response = self.service.dispatch('check_payment', params=params)
            self._check_captured(transaction, response)
            self.assertEqual(
                response['redirect_to'],
                REDIRECT_URL['redirect_success_url'])
        else:
            with self.assertRaises(UserError):
                response = self.service.dispatch(
                    'check_payment', params=params)
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


class ShopinvaderAdyenCase(ShopinvaderAdyenCommonCase, AdyenScenario):
    __metaclass__ = PaymentScenarioType
    _test_path = dirname(__file__)
