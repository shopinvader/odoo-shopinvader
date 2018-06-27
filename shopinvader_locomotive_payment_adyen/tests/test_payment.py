# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_payment_adyen.tests.test_payment import (
    ShopinvaderAdyenCommonCase,
    AdyenScenario,
    REDIRECT_URL,
    SHOPPER_IP,
    ACCEPT_HEADER,
    USER_AGENT)
from os.path import dirname


CLIENT_HEADER = {
    'ACCEPT': ACCEPT_HEADER,
    'USER_AGENT': USER_AGENT,
    'IP': SHOPPER_IP,
    }


class ShopinvaderLocoAdyenCase(ShopinvaderAdyenCommonCase, AdyenScenario):

    def __init__(self, *args, **kwargs):
        super(ShopinvaderAdyenCommonCase, self).__init__(*args, **kwargs)
        self._decorate_test(dirname(__file__))

    def setUp(self, *args, **kwargs):
        super(ShopinvaderLocoAdyenCase, self).setUp(*args, **kwargs)
        with self.work_on_services(
                partner=self.partner,
                shopinvader_session=self.shopinvader_session,
                client_header=CLIENT_HEADER) as work:
            self.service = work.component(usage='cart')

    def _prepare_transaction_params(self, card):
        params = REDIRECT_URL.copy()
        params['token'] = self._get_encrypted_card(card)
        return params

    def _prepare_transaction_return_params(self, transaction, pares):
        return {
            'MD': transaction.meta['MD'],
            'PaRes': pares,
            'provider_name': 'adyen',
            }
