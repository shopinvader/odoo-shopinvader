# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class PaymentService(models.Model):
    _inherit = 'payment.service.paypal'

    def _validator(self):
        return {
            'action': {'type': 'string', 'allowed': ['create']},
            'redirect_cancel_url': {'type': 'string'},
            'redirect_success_url': {'type': 'string'},
            }

    def _process_payment_params(self, cart, params):
        if params['action'] == 'create':
            params['cancel_url'] = params.get('redirect_cancel_url')
            transaction = self.generate(cart, **params)
            return {'redirect_to': transaction.url}
        return {}

    def _return_validator(self):
        return {'paymentId': {'type': 'string'}}

    def _transaction_match(self, params):
        return 'paymentId' in params

    def _get_transaction_from_return(self, params):
        return self.env['gateway.transaction'].search([
            ('external_id', '=', params['paymentId']),
            ('state', '=', 'pending')])
