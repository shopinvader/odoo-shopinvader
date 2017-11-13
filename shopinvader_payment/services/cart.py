# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import Component
from odoo.exceptions import UserError
from odoo.tools.translate import _


class CartService(Component):
    _inherit = 'shopinvader.cart.service'

    def _update(self, params):
        payment_params = params.pop('payment_params', None)
        response = super(CartService, self)._update(params)
        if payment_params:
            cart = self._get()
            provider = cart.payment_mode_id.provider
            if not provider:
                raise UserError(
                    _("The payment method selected does not "
                      "need payment_params"))
            else:
                provider_name = provider.replace('payment.service.', '')
                provider_params = payment_params.pop(provider_name, {})
                provider_params['return_url'] = "%s/%s" % (
                    self.collection.location,
                    '_store/check_transaction')
                response.update(
                    self.env[provider]._process_payment_params(
                        cart, provider_params))
        return response


    def _validator_update(self):
        res = super(CartService, self)._validator_update()
        res['payment_params'] = self._get_payment_validator()
        return res

    def _get_payment_validator(self):
        validator = {
            'type': 'dict',
            'schema': {}
            }
        for provider in self.env['payment.service']._get_all_provider():
            name = provider.replace('payment.service.', '')
            if hasattr(self.env[provider], '_validator'):
                validator['schema'][name] = {
                    'type': 'dict',
                    'schema': self.env[provider]._validator()
                    }
        return validator

    def _to_json(self, cart):
        res = super(CartService, self)._to_json(cart)
        if cart:
            res.update({
                'available_payment_method_ids':
                    self._get_available_payment_method(),
            })
        return res

    def _prepare_payment(self, method):
        return {
            'id': method.payment_mode_id.id,
            'name': method.payment_mode_id.name,
            'code': method.code,
            'description': method.description,
            }

    def _get_available_payment_method(self):
        methods = []
        for method in self.collection.payment_method_ids:
            methods.append(self._prepare_payment(method))
        return methods
