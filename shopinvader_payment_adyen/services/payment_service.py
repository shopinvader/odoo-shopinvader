# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class PaymentServiceAdyen(Component):
    _inherit = 'payment.service.adyen'

    def _validator_add_payment(self):
        return {
            'token': {'type': 'string'},
            'redirect_success_url': {'type': 'string'},
            'redirect_cancel_url': {'type': 'string'},
            'accept_header': {'type': 'string'},
            'user_agent': {'type': 'string'},
            'shopper_ip': {'type': 'string'},
            }

    def _validator_check_payment(self):
        return {
            'md': {'type': 'string'},
            'pares': {'type': 'string'},
            'accept_header': {'type': 'string'},
            'user_agent': {'type': 'string'},
            'shopper_ip': {'type': 'string'},
            }
