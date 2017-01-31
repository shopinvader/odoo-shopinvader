# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import http
from openerp.http import request
from .main import rjson, ShoptorController
from ..services.cart import CartService
from ..services.cart_item import CartItemService


class CartController(ShoptorController):

    @http.route('/shoptor/cart', methods=['GET'], auth="shoptor")
    @http.route('/shoptor/cart/<cart_id>', methods=['PUT'], auth="shoptor")
    def cart(self, **params):
        method = request.httprequest.method
        cart = self._get_service(CartService)
        if method == 'GET':
            res = cart.get(params)
        elif method == 'PUT':
            res = cart.update(params)
        return rjson(res)

    @http.route('/shoptor/cart/item',
                methods=['POST', 'PUT', 'DELETE'],
                auth="shoptor")
    def item(self, **params):
        method = request.httprequest.method
        item = self._get_service(CartItemService)
        if method == 'POST':
            res = item.create(params)
        elif method == 'PUT':
            res = item.update(params)
        elif method == 'DELETE':
            res = item.delete(params)
        return rjson(res)
