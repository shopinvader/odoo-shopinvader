# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .helper import to_int, secure_params
from .abstract_sale import AbstractSaleService
from .contact import ContactService
from .customer import CustomerService
from openerp.addons.connector_locomotivecms.backend import locomotive
from openerp.tools.translate import _
from openerp.exceptions import MissingError, Warning as UserError


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
        payment_params = params.pop('payment_params', None)
        cart = self._get(params.pop('id'))
        # Process use_different_invoice_address
        # before processing the invoice and billing address
        if 'use_different_invoice_address' in params:
            cart.use_different_invoice_address\
                = params.pop('use_different_invoice_address')
        if 'payment_method_id' in params:
            self._check_valid_payment_method(params['payment_method_id'])
        if not self.partner:
            self._set_anonymous_partner(params)
        elif params.pop('assign_partner', None):
            params['partner_id'] = self.partner.id
        if params:
            cart.write(params)
        if 'carrier_id' in params:
            cart.delivery_set()
        elif 'shipping_address_id' in params:
            # If we change the shipping address we update
            # the current carrier
            cart.carrier_id = self._get_available_carrier(cart)[0]
            cart.delivery_set()
        if payment_params:
            provider = cart.payment_method_id.provider
            if not provider:
                raise UserError(
                    _("The payment method selected do not "
                      "need payment_params"))
            else:
                provider_name = provider.replace('payment.service.', '')
                self.env[provider]._process_payment_params(
                    cart, payment_params.pop(provider_name, {}))
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
            'assign_partner': {'type': 'boolean'},
            'carrier_id': {'coerce': to_int, 'nullable': True},
            'use_different_invoice_address': {'type': 'boolean'},
            'cart_state': {'type': 'string'},
            'anonymous_email': {'type': 'string'},
            'payment_method_id': {'coerce': to_int},
            'payment_params': self._get_payment_validator(),
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

    def _parser_transaction(self):
        return ['url']

    def _parser(self):
        res = super(CartService, self)._parser()
        res.append(('current_transaction_id', self._parser_transaction()))
        return res

    def _to_json(self, cart):
        res = super(CartService, self)._to_json(cart)[0]
        res['available_carriers'] = self._get_available_carrier(cart)
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
                raise UserError(_(
                    "Invoice address can not be set before "
                    "the shipping address"))
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
            raise MissingError(_('The cart %s do not exist' % cart_id))
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

    def _check_valid_payment_method(self, method_id):
        if method_id not in self.backend_record.payment_method_ids.mapped(
                'payment_method_id.id'):
            raise UserError(_('Payment method id invalid'))
