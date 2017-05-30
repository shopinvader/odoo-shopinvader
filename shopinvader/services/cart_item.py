# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .helper import to_int, secure_params, ShopinvaderService
from ..backend import shopinvader
from .cart import CartService
from werkzeug.exceptions import NotFound


@shopinvader
class CartItemService(ShopinvaderService):
    _model_name = 'sale.order.line'

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it by using the decorator
    # secure params and the linked validator !

    @secure_params
    def create(self, params):
        cart_service = self.service_for(CartService)
        cart = cart_service._get()
        if not cart:
            cart = cart_service._create_empty_cart()
        existing_item = self._check_existing_cart_item(params, cart)
        if existing_item:
            existing_item.product_uom_qty += params['item_qty']
            cart.recalculate_prices()
        else:
            vals = self._prepare_cart_item(params, cart)
            self.env['sale.order.line'].create(vals)
        return cart_service._to_json(cart)

    @secure_params
    def update(self, params):
        item = self._get_cart_item(params)
        item.product_uom_qty = params['item_qty']
        item.order_id.recalculate_prices()
        cart_service = self.service_for(CartService)
        cart = cart_service._get()
        return cart_service._to_json(cart)

    @secure_params
    def delete(self, params):
        item = self._get_cart_item(params)
        item.unlink()
        cart_service = self.service_for(CartService)
        cart = cart_service._get()
        return cart_service._to_json(cart)

    # Validator
    def _validator_create(self):
        return {
            'product_id': {'coerce': to_int, 'required': True},
            'item_qty': {'coerce': float, 'required': True},
            }

    def _validator_update(self):
        return {
            'item_id': {'coerce': to_int, 'required': True},
            'item_qty': {'coerce': float, 'required': True},
            }

    def _validator_delete(self):
        return {
            'item_id': {'coerce': to_int, 'required': True},
            }

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _get_cart_item(self, params):
        # We search the line based on the item id and the cart id
        # indeed the item_id information is given by the
        # end user (untrusted data) and the cart id by the
        # locomotive server (trusted data)
        item = self.env['sale.order.line'].search([
            ('id', '=', params['item_id']),
            ('order_id', '=', self.cart_id),
            ])
        if not item:
            raise NotFound('No cart item found with id %s' % params['item_id'])
        return item

    def _check_existing_cart_item(self, params, cart):
        return self.env['sale.order.line'].search([
            ('order_id', '=', cart.id),
            ('product_id', '=', params['product_id'])
            ])

    def _prepare_cart_item(self, params, cart):
        return {
            'product_id': params['product_id'],
            'product_uom_qty': params['item_qty'],
            'order_id': cart.id,
            }
