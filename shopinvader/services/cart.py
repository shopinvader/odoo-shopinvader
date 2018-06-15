# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component
from odoo.exceptions import UserError
from odoo.tools.translate import _
from werkzeug.exceptions import NotFound

_logger = logging.getLogger(__name__)


class CartService(Component):
    _inherit = 'shopinvader.abstract.sale.service'
    _name = 'shopinvader.cart.service'
    _usage = 'cart'

    @property
    def cart_id(self):
        return self.shopinvader_session.get('cart_id', 0)

    # The following method are 'public' and can be called from the controller.

    def search(self):
        """Return the cart that have been set in the session or
           search an existing cart for the current partner"""
        return self._to_json(self._get())

    def update(self, **params):
        response = self._update(params)
        cart = self._get()
        if response.get('action_confirm_cart'):
            # TODO improve me, it will be better to block the cart
            # confirmation if the user have set manually the end step
            # and the payment method do not support it
            # the best will be to have a params on the payment method
            return self._confirm_cart(cart)
        elif response.get('redirect_to'):
            return response
        else:
            return self._to_json(cart)

    def add_item(self, **params):
        cart = self._get()
        if not cart:
            cart = self._create_empty_cart()
        self._add_item(cart, params)
        return self._to_json(cart)

    def update_item(self, **params):
        self._update_item(params)
        cart = self._get()
        return self._to_json(cart)

    def delete_item(self, **params):
        self._delete_item(params)
        cart = self._get()
        return self._to_json(cart)

    # Validator
    @property
    def _search_request_schema(self):
        return {}

    def _subvalidator_shipping(self):
        return {
            'type': 'dict',
            'schema': {
                'address': {
                    'type': 'dict',
                    'schema': {'id': {'coerce': to_int}},
                    }
                }
            }

    def _subvalidator_invoicing(self):
        return {
            'type': 'dict',
            'schema': {
                'address': {
                    'type': 'dict',
                    'schema': {'id': {'coerce': to_int}},
                    }
                }
            }

    def _subvalidator_step(self):
        return {
            'type': 'dict',
            'schema': {
                'current': {'type': 'string'},
                'next': {'type': 'string'},
                }
        }

    @property
    def _update_request_schema(self):
        return {
            'step': self._subvalidator_step(),
            'shipping': self._subvalidator_shipping(),
            'invoicing': self._subvalidator_invoicing(),
            'note': {'type': 'string'},
        }

    @property
    def _add_item_request_schema(self):
        return {
            'product_id': {'coerce': to_int, 'required': True},
            'item_qty': {'coerce': float, 'required': True},
        }

    @property
    def _update_item_request_schema(self):
        return {
            'item_id': {'coerce': to_int, 'required': True},
            'item_qty': {'coerce': float, 'required': True},
        }

    @property
    def _delete_item_request_schema(self):
        return {
            'item_id': {'coerce': to_int, 'required': True},
        }
    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _build_common_response_schema(self):
        """
        It's quite long to inherit the common response schema for this
        shopinvader cart.
        So to automatically update the schema, just inherits this function
        to add a new item into the list.
        An item is a tuple: (1, 2, 3)
        1 (string): key of the new sub-schema; ex: images
        2 (string): where to put the new key; ex: data/lines/items/product
        3 (dict):  dict related to the new images schema
        The _common_response_schema will automatically detects if there is a
        schema key and go down if necessary.
        Ex: into your second item of the tuple, just specify
        data/lines/items/product and not data/schema/lines/schema/schema/...
        :return: list of tuple
        """
        return []

    # Response validator
    def _common_response_schema(self):
        address_schema = {
            'type': 'dict',
            'nullable': True,
            'required': False,
            'schema': {
                'address_type': {
                    'type': ['boolean', 'string'],
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
                # 'state': {
                #     'type': 'string',
                #     'nullable': True,
                # },
                'state': {
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
        amount_schema = {
            'type': 'dict',
            'nullable': True,
            'schema': {
                'tax': {
                    'type': 'float',
                    'required': True,
                },
                'total': {
                    'type': 'float',
                    'required': True,
                },
                'untaxed': {
                    'type': 'float',
                    'required': True,
                },
            },
        }
        product_schema = {
            'type': 'dict',
            'nullable': True,
            'schema': {
                'id': {
                    'type': 'integer',
                },
                'model': {
                    'type': 'dict',
                    'nullable': True,
                    'schema': {
                        'name': {
                            'type': 'string',
                            'required': True,
                        },
                    },
                },
                'name': {
                    'type': 'string',
                },
                'short_name': {
                    'type': 'string',
                    'nullable': True,
                },
                'sku': {
                    'type': 'string',
                },
                'url_key': {
                    'type': 'string',
                },
            },
        }
        line_schema = {
            'type': 'dict',
            'nullable': True,
            'schema': {
                'amount': amount_schema,
                'count': {
                    'type': 'float',
                },
                'items': {
                    'type': 'list',
                    'required': True,
                    'schema': {
                        'type': 'dict',
                        'schema': {
                            'amount': {
                                'type': 'dict',
                                'nullable': True,
                                'schema': {
                                    'price': {
                                        'type': 'float',
                                        'required': True,
                                    },
                                    'tax': {
                                        'type': 'float',
                                        'required': True,
                                    },
                                    'total': {
                                        'type': 'float',
                                        'required': True,
                                    },
                                    'untaxed': {
                                        'type': 'float',
                                        'required': True,
                                    },
                                },
                            },
                            'discount': {
                                'type': 'dict',
                                'nullable': True,
                                'schema': {
                                    'rate': {
                                        'type': 'float',
                                        'required': True,
                                    },
                                },
                            },
                            'product': product_schema,
                            'qty': {
                                'type': 'float',
                                'required': True,
                            },
                            'id': {
                                'type': 'integer',
                            },
                        },
                    },
                }
            },
        }
        data_schema = {
            'type': 'dict',
            'schema': {
                'amount': amount_schema,
                'date': {
                    'type': 'string',
                },
                'id': {
                    'type': 'integer',
                    'required': True,
                },
                'invoicing': {
                    'type': 'dict',
                    'nullable': True,
                    'schema': {
                        'address': address_schema,
                    },
                },
                'lines': line_schema,
                'name': {
                    'type': 'string',
                    'required': True,
                },
                'shipping': {
                    'type': 'dict',
                    'nullable': True,
                    'schema': {
                        'address': address_schema,
                    },
                },
                'state': {
                    'type': 'string',
                    'required': True,
                },
                'step': {
                    'type': 'dict',
                    'nullable': True,
                    'schema': {
                        'current': {
                            'type': ['string', 'boolean'],
                            'required': True,
                        },
                        'done': {
                            'type': 'list',
                            'required': True,
                        },
                    },
                },
            }
        }
        schema = {
            'store_cache': {
                'type': 'dict',
                'nullable': True,
                'schema': {
                    'cart': {
                        'type': 'dict',
                        'nullable': True,
                    },
                    'last_sale': data_schema,
                },
            },
            'set_session': {
                'type': 'dict',
                'schema': {
                    'cart_id': {
                        'type': 'integer',
                        'required': True,
                    },
                },
            },
            'data': data_schema,
        }
        # Instead of always inherit this function, add every items
        # specified by inheriting the _build_common_response_schema() function.
        for item in self._build_common_response_schema():
            key, schema_hierarchy, new_schema = item
            target = schema
            if schema_hierarchy:
                for schema_key in schema_hierarchy.split('/'):
                    target = target.get(schema_key, {})
                    while 'schema' in target:
                        target = target.get('schema', {})
            target.update({
                key: new_schema,
            })
        return schema

    @property
    def _create_response_schema(self):
        return self._common_response_schema()

    @property
    def _update_response_schema(self):
        return self._common_response_schema()

    @property
    def _add_item_response_schema(self):
        return self._common_response_schema()

    @property
    def _delete_item_response_schema(self):
        return self._common_response_schema()

    @property
    def _update_item_response_schema(self):
        return self._common_response_schema()

    def _add_item(self, cart, params):
        existing_item = self._check_existing_cart_item(params, cart)
        if existing_item:
            existing_item.product_uom_qty += params['item_qty']
            existing_item.reset_price_tax()
        else:
            vals = self._prepare_cart_item(params, cart)
            self.env['sale.order.line'].create(vals)

    def _update_item(self, params):
        item = self._get_cart_item(params)
        item.product_uom_qty = params['item_qty']
        item.reset_price_tax()

    def _delete_item(self, params):
        item = self._get_cart_item(params)
        item.unlink()

    def _prepare_shipping(self, shipping, params):
        if 'address' in shipping:
            address = shipping['address']
            # By default we always set the invoice address with the
            # shipping address, if you want a different invoice address
            # just pass it
            params['partner_shipping_id'] = address['id']
            params['partner_invoice_id'] = params['partner_shipping_id']

    def _prepare_invoicing(self, invoicing, params):
        if 'address' in invoicing:
            params['partner_invoice_id'] = invoicing['address']['id']

    def _prepare_step(self, step, params):
        if 'next' in step:
            params['current_step_id'] =\
                self._get_step_from_code(step['next']).id
        if 'current' in step:
            params['done_step_ids'] =\
                [(4, self._get_step_from_code(step['current']).id, 0)]

    def _update(self, params):
        action_confirm_cart = False
        cart = self._get()

        if 'shipping' in params:
            self._prepare_shipping(params.pop('shipping'), params)
        if 'invoicing' in params:
            self._prepare_invoicing(params.pop('invoicing'), params)
        if 'step' in params:
            self._prepare_step(params.pop('step'), params)
            if params.get('current_step_id') ==\
                    self.shopinvader_backend.last_step_id.id:
                action_confirm_cart = True
        if params:
            cart.write_with_onchange(params)
        return {'action_confirm_cart': action_confirm_cart}

    def _get_step_from_code(self, code):
        step = self.env['shopinvader.cart.step'].search([('code', '=', code)])
        if not step:
            raise UserError(_('Invalid step code %s') % code)
        else:
            return step

    def _to_json(self, cart):
        if not cart:
            return {'data': {}, 'store_cache': {'cart': {}}}
        res = super(CartService, self)._to_json(cart)[0]
        return {
            'data': res,
            'set_session': {'cart_id': res['id']},
            'store_cache': {'cart': res},
            }

    def _get(self):
        domain = [
            ('typology', '=', 'cart'),
            ('shopinvader_backend_id', '=', self.shopinvader_backend.id),
            ]
        cart = self.env['sale.order'].search(
            domain + [('id', '=', self.cart_id)])
        if cart:
            return cart
        elif self.partner:
            domain.append(('partner_id', '=', self.partner.id))
            return self.env['sale.order'].search(domain, limit=1)

    def _create_empty_cart(self):
        vals = self._prepare_cart()
        return self.env['sale.order'].create(vals)

    def _prepare_cart(self):
        partner = self.partner or self.shopinvader_backend.anonymous_partner_id
        vals = {
            'typology': 'cart',
            'partner_id': partner.id,
            'partner_shipping_id': partner.id,
            'partner_invoice_id': partner.id,
            'shopinvader_backend_id': self.shopinvader_backend.id,
            }
        vals.update(self.env['sale.order'].play_onchanges(vals, vals.keys()))
        if self.shopinvader_backend.sequence_id:
            vals['name'] = self.shopinvader_backend.sequence_id._next()
        return vals

    def _get_onchange_trigger_fields(self):
        return ['partner_id', 'partner_shipping_id', 'partner_invoice_id']

    def _check_call_onchange(self, params):
        onchange_fields = self._get_onchange_trigger_fields()
        for changed_field in params.keys():
            if changed_field in onchange_fields:
                return True
        return False

    def _confirm_cart(self, cart):
        cart.action_confirm_cart()
        res = self._to_json(cart)
        res.update({
            'store_cache': {'last_sale': res['data'], 'cart': {}},
            'set_session': {'cart_id': 0},
            })
        return res

    def _get_cart_item(self, params):
        # We search the line based on the item id and the cart id
        # indeed the item_id information is given by the
        # end user (untrusted data) and the cart id by the
        # locomotive server (trusted data)
        item = self.env['sale.order.line'].search([
            ('id', '=', params['item_id']),
            ('order_id', '=', self.cart_id),
            ])
        if not item:
            raise NotFound('No cart item found with id %s' % params['item_id'])
        return item

    def _check_existing_cart_item(self, params, cart):
        return self.env['sale.order.line'].search([
            ('order_id', '=', cart.id),
            ('product_id', '=', params['product_id'])
            ])

    def _prepare_cart_item(self, params, cart):
        return {
            'product_id': params['product_id'],
            'product_uom_qty': params['item_qty'],
            'order_id': cart.id,
        }
