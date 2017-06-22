# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .helper import to_int, to_bool, secure_params
from .abstract_sale import AbstractSaleService
from .contact import ContactService
from .customer import CustomerService
from ..backend import shopinvader
from openerp.tools.translate import _
from openerp.exceptions import Warning as UserError


@shopinvader
class CartService(AbstractSaleService):
    _model_name = 'sale.order'

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it !

    @secure_params
    def list(self, params):
        """Return the cart that have been set in the session or
           search an existing cart for the current partner"""
        return self._to_json(self._get())

    @secure_params
    def get(self, params):
        return self.list()

    # TODO REFACTOR too many line of code here
    @secure_params
    def update(self, params):
        payment_params = params.pop('payment_params', None)
        cart = self._get()
        # Process use_different_invoice_address
        # before processing the invoice and billing address
        if 'use_different_invoice_address' in params:
            cart.use_different_invoice_address\
                = params.pop('use_different_invoice_address')
        if 'payment_method_id' in params:
            self._check_valid_payment_method(params['payment_method_id'])
            params = self.env['sale.order'].play_onchanges(
                params, ['payment_method_id'])
        if not self.partner:
            self._set_anonymous_partner(params)
        else:
            if params.pop('assign_partner', None):
                params['partner_id'] = self.partner.id
            for key in ('partner_shipping', 'partner_invoice'):
                if key in params:
                    params['%s_id' % key] = params.pop(key)['id']
        recompute_price = False
        if self._check_call_onchange(params):
            if 'partner_id' not in params:
                params['partner_id'] = self.partner.id
            params['order_line'] = cart.order_line
            params = self.env['sale.order'].play_onchanges(
                params,
                ['partner_id', 'partner_shipping_id', 'fiscal_position',
                 'pricelist_id'])
            # Used only to trigger onchanges so we can delete it afterwards
            del params['order_line']
            if params['pricelist_id'] != cart.pricelist_id.id:
                recompute_price = True
        self._update_cart_step(params)
        if params:
            cart.write(params)
            if recompute_price:
                cart.recalculate_prices()
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
                    _("The payment method selected does not "
                      "need payment_params"))
            else:
                provider_name = provider.replace('payment.service.', '')
                self.env[provider]._process_payment_params(
                    cart, payment_params.pop(provider_name, {}))
        if cart.current_step_id == self.backend.last_step_id:
            cart.action_confirm_cart()
        return self._to_json(cart)

    # Validator
    def _validator_get(self):
        return {}

    def _validator_list(self):
        return {}

    def _validator_update(self):
        res = {
            'assign_partner': {'type': 'boolean', 'coerce': to_bool},
            'carrier_id': {'coerce': to_int, 'nullable': True},
            'use_different_invoice_address': {
                'type': 'boolean', 'coerce': to_bool},
            'current_step': {'type': 'string'},
            'next_step': {'type': 'string'},
            'anonymous_email': {'type': 'string'},
            'payment_method_id': {'coerce': to_int},
            'payment_params': self._get_payment_validator(),
            'note': {'type': 'string'},
        }
        if self.partner:
            res.update({
                'partner_shipping': {
                    'type': 'dict',
                    'schema': {'id': {'coerce': to_int}},
                    },
                'partner_invoice': {
                    'type': 'dict',
                    'schema': {'id': {'coerce': to_int}},
                    },
                })
        else:
            customer_service = self.service_for(CustomerService)
            contact_service = self.service_for(ContactService)
            res.update({
                'partner_shipping': {
                    'type': 'dict',
                    'schema': customer_service._validator_create()},
                'partner_invoice': {
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

    def _get_step_from_code(self, code):
        step = self.env['shopinvader.cart.step'].search([('code', '=', code)])
        if not step:
            raise UserError(_('Invalid step code %s') % code)
        else:
            return step

    def _update_cart_step(self, params):
        if 'next_step' in params:
            params['current_step_id'] = self._get_step_from_code(
                params.pop('next_step')).id
        if 'current_step' in params:
            params['done_step_ids'] = [(4, self._get_step_from_code(
                params.pop('current_step')).id, 0)]

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
        if not cart:
            return {'data': {}, 'store_data': 'cart'}
        res = super(CartService, self)._to_json(cart)[0]
        res.update({
            'available_carriers': self._get_available_carrier(cart),
            'available_payment_method_ids':\
                self._get_available_payment_method(),
            'current_step': cart.current_step_id.code,
            'done_steps': cart.done_step_ids.mapped('code'),
            })
        return {
            'data': res,
            'set_session': {'cart_id': res['id']},
            'store_data': 'cart'}

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
        if 'partner_shipping' in params:
            shipping_contact = params.pop('partner_shipping')
            service_customer = self.service_for(CustomerService)
            customer = service_customer.create(shipping_contact)
            params.update({
                'partner_id': customer['id'],
                'partner_shipping_id': customer['id'],
                })
        if 'partner_invoice' in params:
            invoice_contact = params.pop('partner_invoice')
            if not params.get('partner_shipping_id'):
                raise UserError(_(
                    "Invoice address can not be set before "
                    "the shipping address"))
            else:
                invoice_contact['parent_id'] = params['partner_shipping_id']
                contact = self.env['res.partner'].create(invoice_contact)
                params['partner_invoice_id'] = contact.id

    def _get(self):
        domain = [
            ('typology', '=', 'cart'),
            ('shopinvader_backend_id', '=', self.backend_record.id),
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
        partner = self.partner or self.env.ref('shopinvader.anonymous')
        vals = {
            'typology': 'cart',
            'partner_id': partner.id,
            'partner_shipping_id': partner.id,
            'partner_invoice_id': partner.id,
            'shopinvader_backend_id': self.backend_record.id,
            }
        return self.env['sale.order'].play_onchanges(vals, ['partner_id'])

    def _check_valid_payment_method(self, method_id):
        if method_id not in self.backend_record.payment_method_ids.mapped(
                'payment_method_id.id'):
            raise UserError(_('Payment method id invalid'))

    def _get_onchange_trigger_fields(self):
        return ['partner_id', 'partner_shipping_id', 'partner_invoice_id']

    def _check_call_onchange(self, params):
        onchange_fields = self._get_onchange_trigger_fields()
        for changed_field in params.keys():
            if changed_field in onchange_fields:
                return True
        return False
