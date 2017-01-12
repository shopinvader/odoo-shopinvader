# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from openerp import http
from openerp.http import request
from .main import rjson

# TODO we need to define a good way to process params
# maybe we should implement something like in rails
def to_int(params):
    if params:
        return int(float(params))
    else:
        return None

def to_float(params):
    if params:
        return float(params)
    else:
        return None


class SaleController(http.Controller):

    @http.route('/shoptor/cart/cart', methods=['GET'], auth="shoptor")
    def cart(self, cart_id=None, **kwargs):
        if cart_id:
            cart_id = int(float(cart_id))
        return rjson(request.env['shoptor.cart'].get(
            cart_id=cart_id, **kwargs))

    @http.route('/shoptor/cart/item',
                methods=['POST', 'PUT', 'DELETE'],
                auth="shoptor")
    def item(self, cart_id=None, product_id=None, item_id=None, item_qty=None,
             **kwargs):
        cart_id = to_int(cart_id)
        product_id = to_int(product_id)
        item_id = to_int(item_id)
        item_qty = to_float(item_qty)

        method = request.httprequest.method
        item_obj = request.env['shoptor.cart.item']
        if method == 'POST':
            return rjson(item_obj.create(
                product_id, item_qty, cart_id=cart_id, **kwargs))
        elif method == 'PUT':
            return rjson(item_obj.update(cart_id, item_id, item_qty, **kwargs))
        elif method == 'DELETE':
            return rjson(tem_obj.delete(cart_id, item_id, **kwargs))
        return

    @http.route('/shoptor/orders', methods=['GET'], auth="none")
    def orders(self, per_page=5, page=1):
        # TODO get the right partner
        partner_id = 13470
        per_page = int(per_page)
        page = int(page)
        result = request.env['sale.order'].sudo().get_order_history(
            partner_id, per_page=per_page, page=page)
        return rjson(result)
