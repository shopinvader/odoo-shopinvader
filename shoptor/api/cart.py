# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models
from openerp.http import request


class ShoptorCart(models.Model):
    _name = 'shoptor.cart'

    def _json_parser_cart_order(self):
        return [
            'id',
            'name',
            'amount_total',
            'amount_untaxed',
            ('partner_id', ['id', 'display_name', 'ref']),
            ('order_line', [
                'id',
                ('product_id', ['name', 'id']),
                'price_unit',
                'product_uom_qty',
                'price_subtotal',
                ]),
        ]

    @api.multi
    def _to_json(self, cart):
        return cart.jsonify(self._json_parser_cart_order())

    @api.model
    def _get_existing_cart(self):
        if request.partner_id:
            return self.env['sale.order'].search([
                ('sub_state', '=', 'cart'),
                ('partner_id', '=', request.partner_id),
                ], limit=1)

    @api.model
    def _get_card(self, cart_id=None):
        if not cart_id:
            cart = self._get_existing_cart()
        else:
            cart = self.env['sale.order'].browse(cart_id)
        return cart

    @api.model
    def get(self, cart_id=None, **kwargs):
        cart = self._get_card(cart_id)
        if cart:
            return self._to_json(cart)[0]
        else:
            return {}

    def _prepare_card(self):
        if request.partner_id:
            partner_id = request.partner_id
        else:
            partner_id = 1  # TODO add a fake user
        return {
            'sub_state': 'cart',
            'partner_id': partner_id,
            }
