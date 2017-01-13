# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models
from openerp.http import request
from .helper import to_int, secure_params


class ShoptorCart(models.Model):
    _name = 'shoptor.cart'
    _inherit = 'shoptor.api'

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it !

    @api.model
    @secure_params
    def get(self, params):
        cart = self._get_card(params.get('cart_id'))
        if cart:
            return self._to_json(cart)[0]
        else:
            return {}

    # Validator
    def _validator_get(self):
        return {
            'cart_id': {'coerce': to_int, 'nullable': True},
            }

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _parser_product(self):
        return ['name', 'id']

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
            ('order_line', self._parser_order_line()),
        ]

    def _to_json(self, cart):
        return cart.jsonify(self._parser_cart())

    def _get_existing_cart(self):
        if request.partner_id:
            return self.env['sale.order'].search([
                ('sub_state', '=', 'cart'),
                ('partner_id', '=', request.partner_id),
                ], limit=1)

    def _get_card(self, cart_id=None):
        if not cart_id:
            cart = self._get_existing_cart()
        else:
            cart = self.env['sale.order'].search([('id', '=', cart_id)])
        return cart

    def _prepare_card(self):
        if request.partner_id:
            partner_id = request.partner_id
        else:
            partner_id = 1  # TODO add a fake user
        return {
            'sub_state': 'cart',
            'partner_id': partner_id,
            'locomotive_backend_id': request.backend_id,
            }
