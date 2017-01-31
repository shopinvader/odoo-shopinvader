# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .helper import to_int, secure_params, ShoptorService
from openerp.addons.connector_locomotivecms.backend import locomotive
from .cart import CartService
from werkzeug.exceptions import NotFound


@locomotive
class CartItemService(ShoptorService):
    _model_name = 'sale.order.line'

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it by using the decorator
    # secure params and the linked validator !

    @secure_params
    def create(self, params):
        cart_service = self.service_for(CartService)
        cart = cart_service._get_cart(params)
        if not cart:
            cart = cart_service._create_cart(params.get('partner_email'))
        self.env['sale.order.line'].create({
            'product_id': params['product_id'],
            'product_uom_qty': params['item_qty'],
            'order_id': cart.id,
            })
        return cart_service._to_json(cart)[0]

    @secure_params
    def update(self, params):
        item = self._get_cart_item(params)
        item.product_uom_qty = params['item_qty']
        cart_service = self.service_for(CartService)
        return cart_service.get(params)

    @secure_params
    def delete(self, params):
        item = self._get_cart_item(params)
        item.unlink()
        cart_service = self.service_for(CartService)
        return cart_service.get(params)

    # Validator
    def _validator_create(self):
        return {
            'cart_id': {'coerce': to_int, 'nullable': True},
            'product_id': {'coerce': to_int, 'required': True},
            'item_qty': {'coerce': float, 'required': True},
            'partner_email': {'type': 'string', 'nullable': True},
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

    def _get_cart_item(self, params):
        # We search the line based on the item id and the cart id
        # indeed the item_id information is given by the
        # end user (untrusted data) and the cart id by the
        # locomotive server (trusted data)
        cart_id = params['cart_id']
        item_id = params['item_id']
        item = self.env['sale.order.line'].search([
            ('id', '=', item_id),
            ('order_id', '=', cart_id),
            ])
        if not item:
            raise NotFound('No cart item found with id %s' % item_id)
        return item
