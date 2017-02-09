# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .helper import to_int, secure_params
from .abstract_sale import AbstractSaleService
from .contact import ContactService
from .customer import CustomerService
from openerp.addons.connector_locomotivecms.backend import locomotive
from werkzeug.exceptions import BadRequest, NotFound, Forbidden
from openerp.tools.translate import _


@locomotive
class CartService(AbstractSaleService):
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
        if 'payment_method_id' in params and\
                params['payment_method_id'] not in\
                self.backend_record.payment_method_ids.ids:
            raise BadRequest(_('Payment method id invalid'))
        if not self.partner:
            self._set_anonymous_partner(params)
        if params:
            cart.write(params)
        if 'carrier_id' in params:
            cart.delivery_set()
        elif 'shipping_address_id' in params:
            # If we change the shipping address we update
            # the current carrier
            cart.carrier_id = self._get_available_carrier(cart)[0]
            cart.delivery_set()
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
            'use_different_invoice_address': {'type': 'boolean'},
            'cart_state': {'type': 'string'},
            'anonymous_email': {'type': 'string'},
            'payment_method_id': {'coerce': to_int},
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

    def _prepare_available_carrier(self, carrier):
        return {
            'id': carrier.id,
            'name': carrier.name,
            'description': carrier.description,
            'price': carrier.price,
            }

    def _get_available_carrier(self, cart):
        carriers = cart.with_context(order_id=cart.id)\
            .env['delivery.carrier'].search([])
        res = [self._prepare_available_carrier(carrier)
               for carrier in carriers
               if carrier.available]
        return sorted(res, key=lambda x: (x['price'], x['name']))

    def _to_json(self, cart):
        res = super(CartService, self)._to_json(cart)[0]
        res['available_carriers'] = self._get_available_carrier(cart)
        filtred_lines = [l for l in res['order_line'] if not l['is_delivery']]
        res['order_line'] = filtred_lines
        res['available_payment_method_ids']\
            = self._get_available_payment_method()
        return res

    def _prepare_payment(self, method):
        method = method.payment_method_id
        return {
            'id': method.id,
            'name': method.name,
            'code': method.code,
            'description': method.description,
            }

    def _get_available_payment_method(self):
        methods = []
        for method in self.backend_record.payment_method_ids:
            methods.append(self._prepare_payment(method))
        return methods

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
