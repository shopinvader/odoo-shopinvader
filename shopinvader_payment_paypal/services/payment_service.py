# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class PaymentServicePaypal(Component):
    _inherit = 'payment.service.paypal'

    def _validator_add_payment(self):
        return {
                    'cancel_url': {'type': 'string'},
                    'return_url': {'type': 'string'}
               }

    def _validator_check_payment(self): #  TODO
        return {'source': {'type': 'string'}}
