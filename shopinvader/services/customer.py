# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CustomerService(Component):
    _inherit = 'base.shopinvader.service'
    _name = 'shopinvader.customer.service'
    _usage = 'customer'

    # The following method are 'public' and can be called from the controller.
    def get(self):
        if self.partner:
            address = self.component(usage='addresses')
            customer = address._to_json(self.partner)[0]
            return {
                'data': customer,
                'store_cache': {'customer': customer},
                }
        else:
            return {'data': {}}

    def create(self, **params):
        vals = self._prepare_params(params)
        binding = self.env['shopinvader.partner'].create(vals)
        self.work.partner = binding.record_id
        self.shopinvader_backend._send_notification(
            'new_customer_welcome', self.work.partner)
        return self._prepare_create_response(binding)

    def sign_in(self, **params):
        return self._assign_cart_and_get_store_cache()

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before
    def _validator_sign_in(self):
        return {}

    def _validator_create(self):
        address = self.component(usage='addresses')
        schema = address._validator_create()
        schema.update({
            'email': {
                'type': 'string',
                'required': True,
                },
            'external_id': {
                'type': 'string',
                'required': True,
                },
            'vat': {
                'type': 'string',
                'required': False,
                },
            })
        return schema

    def _prepare_params(self, params):
        address = self.component(usage='addresses')
        params = address._prepare_params(params)
        params.update({
            'backend_id': self.shopinvader_backend.id,
            'property_product_pricelist':\
                self.shopinvader_backend.pricelist_id.id,
            })
        if params.get('vat'):
            params['is_company'] = True
        return params

    def _get_and_assign_cart(self):
        cart_service = self.component(usage='cart')
        cart = cart_service._get()
        if cart:
            if self.partner and cart.partner_id != self.partner:
                # we need to affect the cart to the partner
                cart.write_with_onchange({
                    'partner_id': self.partner.id,
                    'partner_shipping_id': self.partner.id,
                    'partner_invoice_id': self.partner.id,
                    })
            return cart_service._to_json(cart)['data']
        else:
            return {}

    def _assign_cart_and_get_store_cache(self):
        address = self.component(usage='addresses')
        cart = self._get_and_assign_cart()
        result = {
            'store_cache': {
                'cart': cart,
                'customer': address._to_json(self.partner)[0],
                },
            }
        if cart:
            result['set_session'] = {'cart_id': cart['id']}
        return result

    def _prepare_create_response(self, binding):
        response = self._assign_cart_and_get_store_cache()
        response['data'] = {
            'id': self.partner.id,
            'name': self.partner.name,
        }
        return response
