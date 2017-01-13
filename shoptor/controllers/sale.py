# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from openerp import http
from openerp.http import request
from .main import rjson


class SaleController(http.Controller):

    @http.route('/shoptor/cart/cart', methods=['GET'], auth="shoptor")
    def cart(self, **params):
        return rjson(request.env['shoptor.cart'].get(params))

    @http.route('/shoptor/cart/item',
                methods=['POST', 'PUT', 'DELETE'],
                auth="shoptor")
    def item(self, **params):
        method = request.httprequest.method
        item_obj = request.env['shoptor.cart.item']
        if method == 'POST':
            res = item_obj.create(params)
        elif method == 'PUT':
            res = item_obj.update(params)
        elif method == 'DELETE':
            res = item_obj.delete(params)
        return rjson(res)

    @http.route('/shoptor/orders', methods=['GET'], auth="none")
    def orders(self, per_page=5, page=1):
        # TODO get the right partner
        partner_id = 13470
        per_page = int(per_page)
        page = int(page)
        result = request.env['sale.order'].sudo().get_order_history(
            partner_id, per_page=per_page, page=page)
        return rjson(result)
