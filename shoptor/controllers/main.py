# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from openerp import http
from openerp.http import request


class MyController(http.Controller):

    def _response_json(self, result):
        return request.make_response(
            json.dumps(result),
            headers={'Content-Type': 'application/json'})

    def _get_cart(self, session=None, email=None):
        # TODO check if session or email are here
        # TODO set domain
        domain = [('id', '=', 210049)]
        return request.env['sale.order'].sudo().search(domain)

    @http.route('/shoptor/cart/cart', methods=['GET'], auth="none")
    def cart(self, session=None, email=None):
        cart = self._get_cart(session, email)
        return self._response_json(cart.to_json_cart()[0])

    @http.route('/shoptor/cart/item',
                methods=['POST', 'PUT', 'DELETE'],
                auth="none")
    def update_item_qty(self, session=None, email=None, item_qty=None,
                        item_id=None, product_id=None):
        cart = self._get_cart(session, email)
        method = request.httprequest.method
        if request.httprequest.method == 'POST':
            request.env['sale.order.line'].create({
                'product_id': product_id,
                'product_uom_qty': item_qty,
                'order_id': cart.id,
                })
        else:
            for line in cart.order_line:
                if line.id == int(item_id):
                    if method == 'PUT':
                        line.product_uom_qty = int(item_qty)
                    elif method == 'DELETE':
                        line.unlink()
                    else:
                        raise NotImplemented
                    break
        return self._response_json(cart.to_json_cart()[0])

    @http.route('/shoptor/orders', methods=['GET'], auth="none")
    def orders(self, session=None, email=None, per_page=5, page=1):
        # TODO get the right partner
        partner_id = 13470
        per_page = int(per_page)
        page = int(page)
        result = request.env['sale.order'].sudo().get_order_history(
            partner_id, per_page=per_page, page=page)
        return self._response_json(result)
