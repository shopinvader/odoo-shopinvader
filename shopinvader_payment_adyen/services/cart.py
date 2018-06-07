# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).



from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = 'shopinvader.cart.service'

    def _execute_payment_action(
            self, provider_name, transaction, cart, params):
        if provider_name == 'adyen' and transaction.url:
            cart = self._get()
            res = self._to_json(cart)
            res['payment']['adyen_params'] = {
                'MD': transaction.meta['MD'],
                'PaReq': transaction.meta['PaReq'],
                'TermUrl': params['return_url'],
                'IssuerUrl': transaction.url,
                }
            return res
        else:
            return super(CartService, self)._execute_payment_action(
                provider_name, transaction, cart, params)
