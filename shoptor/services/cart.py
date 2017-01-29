# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .helper import to_int, secure_params, ShoptorService
from openerp.addons.connector_locomotivecms.backend import locomotive


@locomotive
class CartService(ShoptorService):
    _model_name = 'sale.order'

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it !

    @secure_params
    def get(self, params):
        cart = self._get_cart(params.get('cart_id'))
        if cart:
            return self._to_json(cart)[0]
        else:
            return {}

    @secure_params
    def update(self, params):
        cart = self._get_card(params.get('cart_id'))
        if cart:
            for key in params:
                if key in ['partner_shipping_id', 'partner_invoice_id']:
                    pass
        else:
            raise NotImplemented

    # Validator
    def _validator_get(self):
        return {
            'cart_id': {'coerce': to_int, 'nullable': True},
            }

    def _validator_address(self):
        return {
            'id': {'coerce': to_int},
            'firstname': {'type': 'string'},
            'lastname': {'type': 'string'},
            'street': {'type': 'string'},
            'street2': {'type': 'string'},
            'zip': {'type': 'string'},
            'city': {'type': 'string'},
            'phone': {'type': 'string'},
            'state_id': {'coerce': to_int},
            'country_id': {'coerce': to_int},
            }

    def _validator_update(self):
        return {
            'cart_id': {'coerce': to_int, 'nullable': True},
            'partner_shipping_id': self._validator_address(),
            'partner_invoice_id': self._validator_address(),
            'carrier_id': {'coerce': to_int, 'nullable': True},
            'payment_method_id': {'coerce': to_int, 'nullable': True},
            'cart_state': {'type': 'string'},
            }

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

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

    def _get_existing_cart(self, partner_email):
        partner = self._get_partner(partner_email)
        return self.env['sale.order'].search([
            ('sub_state', '=', 'cart'),
            ('partner_id', '=', partner.id),
            ], limit=1)

    def _get_cart(self, cart_id=None, partner_email=None):
        if not cart_id and partner_email:
            cart = self._get_existing_cart(partner_email)
        else:
            cart = self.env['sale.order'].search([('id', '=', cart_id)])
        return cart

    def _create_cart(self, email=None):
        vals = self._prepare_cart(email)
        return self.env['sale.order'].create(vals)

    def _prepare_cart(self, partner_email=None):
        if partner_email:
            partner = self._get_partner(partner_email)
        else:
            partner = self.env.ref('shoptor.anonymous')
        return {
            'sub_state': 'cart',
            'partner_id': partner.id,
            'locomotive_backend_id': self.backend_record.id,
            }
