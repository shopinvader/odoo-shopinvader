# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .helper import to_int, secure_params, ShoptorService
from .contact import ContactService
from openerp.addons.connector_locomotivecms.backend import locomotive
from werkzeug.exceptions import BadRequest, NotFound, Forbidden


@locomotive
class CartService(ShoptorService):
    _model_name = 'sale.order'

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it !

    @secure_params
    def list(self, params):
        cart = self._search_existing_cart()
        if cart:
            return self._to_json(cart)[0]
        else:
            return {}

    @secure_params
    def get(self, params):
        return self._to_json(self._get(params['id']))[0]

    @secure_params
    def update(self, params):
        cart = self._get(params.pop('id'))
        # Process use_different_invoice_address
        # before processing the invoice and billing address
        if 'use_different_invoice_address' in params:
            cart.use_different_invoice_address\
                = params.pop('use_different_invoice_address')

        if 'partner_id' in params and params['partner_id'] != self.partner.id:
            raise Forbidden(
                "Partner can not be set to %s"
                % params['partner_id'])
        else:
            # TODO
            pass
        if not self.partner:
            for key in ['partner_shipping_id', 'partner_invoice_id']:
                if key in params:
                    address = params.pop(key)
                    self._set_address_for_anonymous_partner(key, address, cart)
        if params:
            cart.write(params)

    # Validator
    def _validator_get(self):
        return {
            'id': {'coerce': to_int},
            }

    def _validator_list(self):
        return {}

    def _validator_address(self):
        if self.partner:
            return {'coerce': to_int}
        else:
            contact_service = self.service_for(ContactService)
            res = contact_service._validator_create()
            return {'type': 'dict', 'schema': res}

    def _validator_update(self):
        return {
            'id': {'coerce': to_int, 'required': True},
            'partner_id': {'coerce': to_int},
            'partner_shipping_id': self._validator_address(),
            'partner_invoice_id': self._validator_address(),
            'carrier_id': {'coerce': to_int, 'nullable': True},
            'payment_method_id': {'coerce': to_int, 'nullable': True},
            'cart_state': {'type': 'string', 'nullable': True},
            'use_different_invoice_address': {'type': 'boolean'},
            }

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _set_address_for_anonymous_partner(self, key, address, cart):
        if key == 'partner_invoive_id':
            if cart.partner_id == self.env.ref('shoptor.anonymous'):
                raise BadRequest(
                    "Invoice address can not be set before "
                    "the shipping address")
            else:
                address['parent_id'] = cart.partner_id
        contact = self.env['res.partner'].create(address)
        if key == 'partner_shipping_id':
            cart.partner_id = contact.id
        cart[key] = contact.id

    def _parser_product(self):
        fields = ['name', 'id']
        if 'product_code_builder' in self.env.registry._init_modules:
            fields.append('prefix_code')
        return fields

    def _parser_order_line(self):
        parser = [
            'id',
            ('product_id', self._parser_product()),
            'product_url',
            'price_unit',
            'product_uom_qty',
            'price_subtotal',
            'discount',
            ]
        if 'sale_order_line_price_subtotal_gross' in\
                self.env.registry._init_modules:
            parser.append('price_subtotal_gross')
        return parser

    def _parser_partner(self):
        return ['id', 'display_name', 'ref']

    def _parser_cart(self):
        return [
            'id',
            'name',
            'amount_total',
            'amount_untaxed',
            'amount_tax',
            ('partner_id', self._parser_partner()),
            ('partner_shipping_id', self._parser_partner()),
            ('partner_invoice_id', self._parser_partner()),
            ('order_line', self._parser_order_line()),
        ]

    def _to_json(self, cart):
        return cart.jsonify(self._parser_cart())

    def _search_existing_cart(self):
        return self.env['sale.order'].search([
            ('sub_state', '=', 'cart'),
            ('partner_id', '=', self.partner.id),
            ], limit=1)

    def _get(self, cart_id):
        cart = self.env['sale.order'].search([
            ('id', '=', cart_id),
            ('locomotive_backend_id', '=', self.backend_record.id),
            ])
        if not cart:
            raise NotFound('The cart %s do not exist' % cart_id)
        else:
            return cart

    def _create_empty_cart(self):
        vals = self._prepare_cart()
        return self.env['sale.order'].create(vals)

    def _prepare_cart(self):
        partner = self.partner or self.env.ref('shoptor.anonymous')
        return {
            'sub_state': 'cart',
            'partner_id': partner.id,
            'partner_shipping_id': partner.id,
            'partner_invoice_id': partner.id,
            'locomotive_backend_id': self.backend_record.id,
            }
