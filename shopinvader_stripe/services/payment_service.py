# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class PaymentService(models.Model):
    _inherit = 'payment.service.stripe'

    def _validator(self):
        return {
            'source': {'type': 'string'},
            'redirect_success_url': {'type': 'string'},
            'redirect_cancel_url': {'type': 'string'},
            }

    def _process_payment_params(self, cart, payment_params):
        transaction = self.generate(cart, **payment_params)
        if transaction.url:
            return {'redirect_to': transaction.url}
        elif transaction.state in ('succeeded', 'to_capture'):
            return {'action_confirm_cart': True}
        else:
            raise UserError(_('Payment failed please retry'))

    def _return_validator(self):
        return {'source': {'type': 'string'}}

    def _transaction_match(self, params):
        return params.get('source') and params['source'][0:3] == 'src'

    def _get_transaction_from_return(self, params):
        return self.env['gateway.transaction'].search([
            ('external_id', '=', params['source']),
            ('state', '=', 'pending')])
