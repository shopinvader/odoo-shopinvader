# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase
from odoo.addons.payment_gateway_paypal.tests.test_payment import (
    PaypalCommonCase,
    PaypalScenario)
import json
from mock import Mock
from os.path import dirname


REDIRECT_URL = {
    'redirect_cancel_url': 'https://IamGoingToKickYourAssIfYouDoNotPaid.com',
    'redirect_success_url': 'https://ThanksYou.com',
    }


class ShopinvaderPaypalCase(PaypalCommonCase, CommonCase, PaypalScenario):

    def __init__(self, *args, **kwargs):
        super(ShopinvaderPaypalCase, self).__init__(*args, **kwargs)
        self._decorate_test(dirname(__file__))

    def setUp(self, *args, **kwargs):
        super(ShopinvaderPaypalCase, self).setUp(*args, **kwargs)
        self.shopinvader_session = {'cart_id': self.sale.id}
        self.partner = self.sale.partner_id
        self.env['shopinvader.partner'].create({
            'record_id': self.partner.id,
            'external_id': 'ZG9kbw==', #  TODO correct?
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
        pass #  TODO

    def _check_reponse(self, response, redirect=False):
        pass #  TODO

    def _simulate_return(self, transaction):
        return self.service.dispatch('check_payment', params={
            'source': transaction.external_id,
            'provider_name': 'paypal',
            })

    def _test_3d(self, card, success=True, mode='return'):
        pass  # TODO

    def _test_card(self, card, **kwargs):
        response, transaction, source = self._create_transaction(card)
        self._check_captured(transaction, **kwargs)
        self._check_reponse(response)

    def test_create_transaction_3d_not_supported(self):
        response, transaction, source =\
            self._create_transaction('378282246310005')
        self._check_captured(transaction)
        self._check_reponse(response)
