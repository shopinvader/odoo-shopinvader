# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component
from .helper import to_int, secure_params
from odoo.tools.translate import _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class CartService(Component):
    _inherit = 'shopinvader.abstract.sale.service'
    _name = 'shopinvader.cart.service'
    _usage = 'cart.service'

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it !

    @secure_params
    def get(self, params):
        """Return the cart that have been set in the session or
           search an existing cart for the current partner"""
        return self._to_json(self._get())

    # TODO REFACTOR too many line of code here
    @secure_params
    def update(self, params):
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

    def _update(self, params):
        action_confirm_cart = \
            params.get('next_step') == self.collection.last_step_id.code
        cart = self._get()
        if params.get('anonymous_email'):
            self._check_allowed_anonymous_email(cart, params)

        if 'payment_method_id' in params:
            self._check_valid_payment_method(params['payment_method_id'])
        if not self.partner:
            self._set_anonymous_partner(cart, params)
        else:
            if 'partner_shipping' in params:
                # By default we always set the invoice address with the
                # shipping address, if you want a different invoice address
                # just pass it
                params['partner_shipping_id'] = params.pop(
                    'partner_shipping')['id']
                params['partner_invoice_id'] = params['partner_shipping_id']
            if 'partner_invoice' in params:
                params['partner_invoice_id'] = params.pop(
                    'partner_invoice')['id']
        self._update_cart_step(params)
        if params:
            cart.write_with_onchange(params)
        return {'action_confirm_cart': action_confirm_cart}

    # Validator
    def _validator_get(self):
        return {}

    def _validator_update(self):
        res = {
            'carrier_id': {'coerce': to_int, 'nullable': True},
            'current_step': {'type': 'string'},
            'next_step': {'type': 'string'},
            'anonymous_email': {'type': 'string'},
            'payment_method_id': {'coerce': to_int},
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
            address_service = self.component(usage='address.service')
            res.update({
                'partner_shipping': {
                    'type': 'dict',
                    'schema': address_service._validator_create()},
                'partner_invoice': {
                    'type': 'dict',
                    'schema': address_service._validator_create()},
                })
        return res


    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _check_allowed_anonymous_email(self, cart, params):
        if self.collection.restrict_anonymous and\
                self.env['shopinvader.partner'].search([
                    ('backend_id', '=', self.collection.id),
                    ('email', '=', params['anonymous_email']),
                    ]):
            # In that case we want to raise an error to block the process
            # but before we save the anonymous partner to avoid
            # losing this important information
            _logger.debug(
                'An account already exist for %s, block it',
                params['anonymous_email'])
            cart.anonymous_email = params['anonymous_email']
            cart._cr.commit()
            raise UserError(_('An account already exist for this email'))

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

    def _to_json(self, cart):
        if not cart:
            return {'data': {}, 'store_cache': {'cart': {}}}
        res = super(CartService, self)._to_json(cart)[0]
        res.update({
            # TODO MIGRATE in shopinvader_delivery
            # 'available_carriers': cart._get_available_carrier(),
            'current_step': cart.current_step_id.code,
            'done_steps': cart.done_step_ids.mapped('code'),
            })
        return {
            'data': res,
            'set_session': {'cart_id': res['id']},
            'store_cache': {'cart': res},
            }

    def _set_anonymous_partner(self, cart, params):
        if 'partner_shipping' in params:
            shipping_address = params.pop('partner_shipping')
            if params.get('anonymous_email'):
                shipping_address['email'] = params['anonymous_email']
            elif cart.anonymous_email:
                shipping_address['email'] = cart.anonymous_email
            else:
                raise UserError(_('Anonymous Email is missing'))
            partner = self.env['res.partner'].create(shipping_address)
            params.update({
                'partner_id': partner.id,
                'partner_shipping_id': partner.id,
                'partner_invoice_id': partner.id,
                })
        if 'partner_invoice' in params:
            invoice_address = params.pop('partner_invoice')
            if not params.get('partner_shipping_id'):
                raise UserError(_(
                    "Invoice address can not be set before "
                    "the shipping address"))
            else:
                invoice_address['parent_id'] = params['partner_shipping_id']
                address = self.env['res.partner'].create(invoice_address)
                params['partner_invoice_id'] = address.id

    def _get(self):
        domain = [
            ('typology', '=', 'cart'),
            ('shopinvader_backend_id', '=', self.collection.id),
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
        partner = self.partner or self.collection.anonymous_partner_id
        vals = {
            'typology': 'cart',
            'partner_id': partner.id,
            'partner_shipping_id': partner.id,
            'partner_invoice_id': partner.id,
            'shopinvader_backend_id': self.collection.id,
            }
        res = self.env['sale.order']._play_cart_onchange(vals)
        vals.update(res)
        if self.collection.sequence_id:
            vals['name'] = self.collection.sequence_id._next()
        return vals

    def _check_valid_payment_method(self, method_id):
        if method_id not in self.collection.payment_method_ids.mapped(
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

    def _confirm_cart(self, cart):
        cart.action_confirm_cart()
        res = self._to_json(cart)
        res.update({
            'store_cache': {'last_sale': res['data'], 'cart': {}},
            'set_session': {'cart_id': 0},
            })
        return res
