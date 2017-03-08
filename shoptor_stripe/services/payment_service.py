# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models
import json


class PaymentService(models.Model):
    _inherit = 'payment.service.stripe'

    def _validator(self):
        return {
            'token': {'type': 'string'},
            }

    def _process_payment_params(self, cart):
        return self.capture(cart.current_transaction_id)
