# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class PaymentService(models.Model):
    _inherit = 'payment.service.stripe'

    def _validator(self):
        return {
            'source': {'type': 'string'},
            'return_url': {'type': 'string'},
            }

    def _process_payment_params(self, cart, payment_params):
        transaction = self.generate(cart, **payment_params)
        if transaction.url:
            return {'redirect_to': transaction.url}
        else:
            return {}
