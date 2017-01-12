# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models
from openerp.http import request


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
