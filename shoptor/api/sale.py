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


class ShoptorCartItem(models.AbstractModel):
    _name = 'shoptor.cart.item'

    @api.model
    def create(self, product_id, item_qty, cart_id=None, **kwargs):
        cart_obj = self.env['shoptor.cart']
        cart = cart_obj._get_card(cart_id)
        if not cart:
            vals = cart_obj._prepare_card()
            cart = self.env['sale.order'].create(vals)
        self.env['sale.order.line'].create({
            'name': 'TODO',
            'product_id': int(product_id),
            'product_uom_qty': item_qty,
            'order_id': cart.id,
            })
        return cart_obj._to_json(cart)[0]

    @api.model
    def _get_cart_item(self, cart_id, item_id):
        # We search the line based on the item id and the cart id
        # indeed the item_id information is given by the
        # end user (untrusted data) and the cart id by the
        # locomotive server (trusted data)
        item = self.env['sale.order'].search([
            ('id', '=', item_id),
            ('order_id', '=', cart_id),
            ])
        if not item:
            raise # TODO raise access error
        return item

    @api.model
    def update(self, cart_id, item_id, item_qty, **kwargs):
        item = self._get_cart_item(cart_id, item_id)
        item.product_uom_qty = float(item_qty)
        return self.env['shoptor.cart'].get(cart_id)

    def delete(self, cart_id, item_id, **kwargs):
        item = self._get_cart_item(cart_id, item_id)
        item.unlink()
        return self.env['shoptor.cart'].get(cart_id)


class ShoptorOrder(models.AbstractModel):
    _name = 'shoptor.order'

    def _json_parser_history_order(self):
        # photo => url
        return [
            'state',
            'name',
            'date_order',
            ('carrier_id', ['name']),
            'amount_total',
            'amount_tax',
            'amount_untaxed',
            ('partner_shipping_id', [
                'id', 'display_name', 'ref', 'street',
                'street2', 'zip', 'city', 'phone',
                ('state_id', ['name']),
                ('country_id', ['name'])
                ]),
            ('partner_invoice_id', [
                'id', 'display_name', 'ref', 'street',
                'street2', 'zip', 'city', 'phone',
                ('state_id', ['name']),
                ('country_id', ['name'])
                ]),
            ('invoice_ids', ['id', 'number']),
            ('order_line', [
                'id',
                ('product_id', ['name', 'id']),
                'price_unit',
                'product_uom_qty',
                'price_subtotal',
                ]),
        ]


    @api.multi
    def to_json_history(self):
        result = self.jsonify(self._json_parser_history_order())
        status_list = {
            'draft': 'quotation',
            'confirm': 'pending',
            # 'confirm': 'processing',
            'done': 'done',
            'cancel': 'cancel',
            }

        for order in result:
            order.update({
                'shipping_amount_tax_excluded': 10,
                'shipping_amount_tax_included': 12,
                'shipping_tax_amount': 2,
                'tracking': [{
                    'url': 'https://montracking',  # TODO
                    'value': '69DJSEO494394',
                    }],
                'payment_method_id': {'name': 'stripe'},
                'status': status_list.get(order['state'], 'processing'),
            })
            order.pop('state')
            for line in order['order_line']:
                line['product_image_url'] = 'http://todo.jpg'  # TODO
        return result

    @api.model
    def get_order_history(self, partner_id, per_page, page):
        domain = [('partner_id', '=', partner_id)]
        total_count = self.search_count(domain)
        orders = self.search(domain, limit=per_page, offset=per_page*(page-1))
        return {
            'total_count': total_count,
            'nbr_page': total_count/per_page + 1,
            'orders': orders.to_json_history(),
            }
