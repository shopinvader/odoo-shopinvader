# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component

# Locomotive proxy do not implement any logic, it's 100% generic it's just
# pass the data its receive, we need here to map the field and to inject
# header information into params


class PaymentServiceAdyen(Component):
    _inherit = 'payment.service.adyen'

    def _remove_header_params(self, schema):
        for key in ['accept_header', 'user_agent', 'shopper_ip']:
            schema.pop(key)

    def _validator_add_payment(self):
        schema = super(PaymentServiceAdyen, self)._validator_add_payment()
        self._remove_header_params(schema)
        return schema

    def _validator_check_payment(self):
        schema = super(PaymentServiceAdyen, self)._validator_check_payment()
        self._remove_header_params(schema)
        for key in ['MD', 'PaRes']:
            schema[key] = schema.pop(key.lower())
        return schema
