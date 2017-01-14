# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models
from openerp.http import request
from .helper import to_int, secure_params


class ShoptorCartItem(models.AbstractModel):
    _name = 'shoptor.cart.item'
    _inherit = 'shoptor.api'

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it by using the decorator
    # secure params and the linked validator !

    @secure_params
    def create(self, params):
        cart_obj = self.env['shoptor.cart']
        cart = cart_obj._get_card(params['cart_id'])
        if not cart:
            vals = cart_obj._prepare_card()
            cart = self.env['sale.order'].create(vals)
        self.env['sale.order.line'].create({
            'product_id': params['product_id'],
            'product_uom_qty': params['item_qty'],
            'order_id': cart.id,
            })
        return cart_obj._to_json(cart)[0]

    @secure_params
    def update(self, params):
        item = self._get_cart_item(params['cart_id'], params['item_id'])
        item.product_uom_qty = params['item_qty']
        return self.env['shoptor.cart'].get(params)

    @secure_params
    def delete(self, params):
        item = self._get_cart_item(params['cart_id'], params['item_id'])
        item.unlink()
        return self.env['shoptor.cart'].get(params)

    # Validator
    def _validator_create(self):
        return {
            'cart_id': {'coerce': to_int, 'nullable': True},
            'product_id': {'coerce': to_int, 'required': True},
            'item_qty': {'coerce': float, 'required': True},
            }

    def _validator_update(self):
        return {
            'cart_id': {'coerce': to_int, 'required': True},
            'item_id': {'coerce': to_int, 'required': True},
            'item_qty': {'coerce': float, 'required': True},
            }

    def _validator_delete(self):
        return {
            'cart_id': {'coerce': to_int, 'required': True},
            'item_id': {'coerce': to_int, 'required': True},
            }

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    @api.model
    def _get_cart_item(self, cart_id, item_id):
        # We search the line based on the item id and the cart id
        # indeed the item_id information is given by the
        # end user (untrusted data) and the cart id by the
        # locomotive server (trusted data)
        item = self.env['sale.order.line'].search([
            ('id', '=', item_id),
            ('order_id', '=', cart_id),
            ])
        if not item:
            raise # TODO raise access error
        return item
