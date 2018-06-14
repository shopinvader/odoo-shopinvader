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
        external_id = params.pop('external_id')
        params['is_company'] = True
        vals = self._prepare_params(params)
        self.work.partner = self.env['res.partner'].create(vals)
        self.shopinvader_backend._send_notification(
            'new_customer_welcome', self.partner)
        return self._create_shopinvader_binding(external_id)

    def sign_in(self, **params):
        return self._assign_cart_and_get_store_cache()

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    @property
    def _get_request_schema(self):
        return {}

    @property
    def _sign_in_request_schema(self):
        return {}

    @property
    def _create_request_schema(self):
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

    @property
    def _create_response_schema(self):
        data_schema = {
            'type': 'dict',
            'schema': {
                'id': {
                    'type': 'integer',
                    'required': True,
                },
                'name': {
                    'type': 'string',
                },
            }
        }
        customer_schema = {
            'type': 'dict',
            'nullable': True,
            'required': False,
            'schema': {
                'address_type': {
                    'type': 'string',
                },
                'city': {
                    'type': 'string',
                    'nullable': True,
                },
                'country': {
                    'type': 'dict',
                    'nullable': True,
                    'schema': {
                        'name': {
                            'type': 'string',
                            'required': True,
                        },
                        'id': {
                            'type': 'integer',
                            'required': True,
                        },
                    },
                },
                'display_name': {
                    'type': 'string',
                    'nullable': True,
                },
                'id': {
                    'type': 'integer',
                    'nullable': True,
                },
                'is_company': {
                    'type': 'boolean',
                    'nullable': True,
                },
                'name': {
                    'type': 'string',
                    'nullable': True,
                },
                'opt_in': {
                    'type': 'boolean',
                    'nullable': True,
                },
                'opt_out': {
                    'type': 'boolean',
                    'nullable': True,
                },
                'phone': {
                    'type': 'string',
                    'nullable': True,
                },
                'ref': {
                    'type': 'string',
                    'nullable': True,
                },
                'state': {
                    'type': 'string',
                    'nullable': True,
                },
                'street': {
                    'type': 'string',
                    'nullable': True,
                },
                'street2': {
                    'type': 'string',
                    'nullable': True,
                },
                'vat': {
                    'type': 'string',
                    'nullable': True,
                },
                'zip': {
                    'type': 'string',
                    'nullable': True,
                },
            },
        }
        store_cache_schema = {
            'type': 'dict',
            'schema': {
                'cart': {
                    'type': 'dict',
                },
                'customer': customer_schema,
            }
        }
        schema = {
            'store_cache': store_cache_schema,
            'data': data_schema,
        }
        return schema

    def _prepare_params(self, params):
        for key in ['country', 'state']:
            if key in params:
                val = params.pop(key)
                if val.get('id'):
                    params["%s_id" % key] = val['id']
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
        return {
            'store_cache': {
                'cart': self._get_and_assign_cart(),
                'customer': address._to_json(self.partner)[0],
                }
            }

    def _create_shopinvader_binding(self, external_id):
        self.env['shopinvader.partner'].with_context(
            connector_no_export=True).create({
                'backend_id': self.shopinvader_backend.id,
                'external_id': external_id,
                'record_id': self.partner.id,
                })
        response = self._assign_cart_and_get_store_cache()
        response['data'] = {
            'id': self.partner.id,
            'name': self.partner.name,
        }
        return response
