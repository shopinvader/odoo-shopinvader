# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .helper import to_int, secure_params, ShoptorService
from .contact import ContactService
from .customer import CustomerService
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
            return self._to_json(cart)
        else:
            return {}

    @secure_params
    def get(self, params):
        return self._to_json(self._get(params['id']))

    @secure_params
    def update(self, params):
        cart = self._get(params.pop('id'))
        # Process use_different_invoice_address
        # before processing the invoice and billing address
        if 'use_different_invoice_address' in params:
            cart.use_different_invoice_address\
                = params.pop('use_different_invoice_address')

        if 'partner_id' in params and params['partner_id'] != self.partner.id:
            raise Forbidden("Partner can not be set to %s"
                            % params['partner_id'])
        if not self.partner:
            self._set_anonymous_partner(params)
        if params:
            cart.write(params)
        return self._to_json(cart)

    # Validator
    def _validator_get(self):
        return {
            'id': {'coerce': to_int},
            }

    def _validator_list(self):
        return {}

    def _validator_update(self):
        res = {
            'id': {'coerce': to_int, 'required': True},
            'partner_id': {'coerce': to_int},
            'carrier_id': {'coerce': to_int, 'nullable': True},
            'payment_method_id': {'coerce': to_int, 'nullable': True},
            'cart_state': {'type': 'string', 'nullable': True},
            'use_different_invoice_address': {'type': 'boolean'},
            'cart_step': {'type': 'string'},
            'anonymous_email': {'type': 'string'},
            }
        if self.partner:
            res.update({
                'partner_shipping_id': {'coerce': to_int},
                'partner_invoice_id': {'coerce': to_int},
                })
        else:
            customer_service = self.service_for(CustomerService)
            contact_service = self.service_for(ContactService)
            res.update({
                'partner_shipping_id': {
                    'type': 'dict',
                    'schema': customer_service._validator_create()},
                'partner_invoice_id': {
                    'type': 'dict',
                    'schema': contact_service._validator_create()},
                })
        return res

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
            'is_delivery',
            ]
        if 'sale_order_line_price_subtotal_gross' in\
                self.env.registry._init_modules:
            parser.append('price_subtotal_gross')
        return parser

    def _parser_partner(self):
        return ['id', 'display_name', 'ref']

    def _parser_cart(self):
        contact_parser = self.service_for(ContactService)._json_parser()
        return [
            'id',
            'name',
            'amount_total',
            'amount_untaxed',
            'amount_tax',
            'cart_step',
            'anonymous_email',
            ('partner_id', self._parser_partner()),
            ('partner_shipping_id', contact_parser),
            ('partner_invoice_id', contact_parser),
            ('order_line', self._parser_order_line()),
        ]

    def _to_json(self, cart):
        res = cart.jsonify(self._parser_cart())[0]
        carriers = cart.with_context(order_id=cart.id)\
            .env['delivery.carrier'].search([])
        res['available_carriers'] = []
        for carrier in carriers:
            if carrier.available:
                res['available_carriers'].append({
                    'id': carrier.id,
                    'name': carrier.name,
                    'price': carrier.price,
                    })
        filtred_lines = []
        for line in res['order_line']:
            if line['is_delivery']:
                pass
            else:
                filtred_lines.append(line)
        res['order_line'] = filtred_lines
        return res

    def _set_anonymous_partner(self, params):
        if 'partner_shipping_id' in params:
            shipping_contact = params['partner_shipping_id']
            service_customer = self.service_for(CustomerService)
            customer = service_customer.create(shipping_contact)
            params.update({
                'partner_id': customer['id'],
                'partner_shipping_id': customer['id'],
                })
        if 'partner_invoice_id' in params:
            invoice_contact = params['partner_invoice_id']
            if not params.get('partner_shipping_id'):
                raise BadRequest(
                    "Invoice address can not be set before "
                    "the shipping address")
            else:
                invoice_contact['parent_id'] = params['partner_shipping_id']
                contact = self.env['res.partner'].create(invoice_contact)
                params['partner_invoice_id'] = contact.id

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
