# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .helper import to_int, secure_params, ShoptorService
from .contact import ContactService
from openerp.addons.connector_locomotivecms.backend import locomotive


@locomotive
class CartService(ShoptorService):
    _model_name = 'sale.order'

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it !

    @secure_params
    def get(self, params):
        cart = self._get_cart(params)
        if cart:
            return self._to_json(cart)[0]
        else:
            return {}

    @secure_params
    def update(self, params):
        cart = self._get_cart(params)
        if cart:
            partner_email = params.get('partner_email')
            if partner_email:
                partner = self._get_partner(partner_email)
                if cart.partner_id != partner:
                    cart.partner_id = partner
                    cart.anonymous = False
            else:
                partner = None
            # Process use_different_invoice_address
            # before processing the invoice and billing address
            if 'use_different_invoice_address' in params:
                cart.use_different_invoice_address\
                    = params.pop('use_different_invoice_address')

            for key in ['partner_shipping_id', 'partner_invoice_id']:
                if key in params:
                    address = params.pop(key)
                    if not partner_email:
                        self._set_address_for_anonymous_partner(
                            key, address, cart)
                    else:
                        self._set_address_for_logged_partner(
                            key, address, cart, partner_email)
            params.pop('cart_id')
            params.pop('partner_email')
            if params:
                cart.write(params)
        else:
            raise NotImplemented

    # Validator
    def _validator_get(self):
        return {
            'cart_id': {'coerce': to_int, 'nullable': True},
            }

    def _validator_address(self):
        contact_service = self.service_for(ContactService)
        res = contact_service._validator_create()
        res['id'] = {'coerce': to_int, 'nullable': True}
        res.pop('partner_email')
        return {'type': 'dict', 'schema': res}

    def _validator_update(self):
        return {
            'partner_email': {'type': 'string', 'nullable': True},
            'cart_id': {'coerce': to_int, 'nullable': True},
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
        # Be carefull partner is not logged so we have to restrict the
        # edition and creation of address to the current cart
        if 'id' in address:
            if not cart[key].id == address['id']:
                raise
            else:
                cart[key].write(address)
        else:
            if key == 'partner_invoive_id':
                # If we are creating an invoice address
                # We have to link that address to the not logged
                # customer and the invoice address must be set
                # after setting a shipping address
                if cart.partner_id == self.env.ref('shoptor.anonymous'):
                    raise
                else:
                    address['parent_id'] = cart.partner_id
            contact = self.env['res.partner'].create(address)
            if key == 'partner_shipping_id':
                cart.partner_id = contact['id']
            cart[key] = contact['id']

    def _set_address_for_logged_partner(
            self, key, address, cart, partner_email):
        address['partner_email'] = partner_email
        contact_service = self.service_for(ContactService)
        if 'id' in address:
            contact = contact_service.update(address)
        else:
            contact = contact_service.create(address)
        cart[key] = contact['id']

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

    def _get_cart(self, params):
        cart_id = params.get('cart_id')
        partner_email = params.get('partner_email')
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
