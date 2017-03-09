# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models
import json
from openerp.exceptions import Warning as UserError


class PaymentService(models.Model):
    _inherit = 'payment.service.paypal'

    def _validator(self):
        return {
            'action': {'type': 'string', 'allowed': ['create', 'execute']},
            'cancel_url': {'type': 'string'},
            'return_url': {'type': 'string'},
            'payer_id': {'type': 'string'},
            'payment_id': {'type': 'string'},
            }

    def _process_payment_params(self, cart, params):
        if params['action'] == 'create':
           self.generate(
                cart,
                return_url=params.get('return_url'),
                cancel_url=params.get('cancel_url'))
        else:
            transaction = cart.current_transaction_id
            if params['payment_id'] != transaction.external_id:
                raise UserError(_("Wrong Paypal transaction id"))
            return self.capture(transaction, params['payer_id'])
