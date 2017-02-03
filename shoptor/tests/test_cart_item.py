# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ..services.cart_item import CartItemService
from ..services.cart import CartService
from .common import CommonCase


class AbstractItemCase(object):

    def setUp(self, *args, **kwargs):
        super(AbstractItemCase, self).setUp(*args, **kwargs)
        self.product_1 = self.env.ref('product.product_product_4b')
        self.product_2 = self.env.ref('product.product_product_14')

    def add_item(self, cart_id, product_id, qty):
        return self.service.create({
            'cart_id': cart_id,
            'product_id': product_id,
            'item_qty': qty,
            })

    def update_item(self, item_id, qty):
        return self.service.update({
            'cart_id': self.cart.id,
            'item_id': item_id,
            'item_qty': qty,
            })

    def delete_item(self, item_id):
        return self.service.delete({
            'cart_id': self.cart.id,
            'item_id': item_id,
            })

    def check_product_and_qty(self, line, product_id, qty):
        self.assertEqual(line['product_id']['id'], product_id)
        self.assertEqual(line['product_uom_qty'], qty)

    def check_partner(self, cart):
        self.assertEqual(cart['partner_id']['id'], self.partner.id)
        self.assertEqual(cart['partner_shipping_id']['id'], self.partner.id)
        self.assertEqual(cart['partner_invoice_id']['id'], self.partner.id)

    def test_add_item_without_cart(self):
        last_order = self.env['sale.order'].search(
            [], limit=1, order='id desc')
        cart = self.add_item(None, self.product_1.id, 2)
        self.assertGreater(cart['id'], last_order.id)
        self.assertEqual(len(cart['order_line']), 1)
        self.check_product_and_qty(cart['order_line'][0], self.product_1.id, 2)
        self.check_partner(cart)

    def test_add_item_with_an_existing_cart(self):
        cart = self.cart_service.get({'id': self.cart.id})
        nbr_line = len(cart['order_line'])

        cart = self.add_item(self.cart_id, self.product_1.id, 2)
        self.assertEqual(cart['id'], self.cart.id)
        self.assertEqual(len(cart['order_line']), nbr_line + 1)
        self.check_product_and_qty(
            cart['order_line'][-1], self.product_1.id, 2)
        self.check_partner(cart)
        return cart

    def test_update_item(self):
        line_id = self.cart.order_line[0].id
        product_id = self.cart.order_line[0].product_id.id
        cart = self.update_item(line_id, 5)
        self.check_product_and_qty(cart['order_line'][0], product_id, 5)

    def test_delete_item(self):
        cart = self.cart_service.get({'id': self.cart.id})
        nbr_line = len(cart['order_line'])
        cart = self.delete_item(cart['order_line'][0]['id'])
        self.assertEqual(len(cart['order_line']), nbr_line - 1)


class AnonymousItemCase(AbstractItemCase, CommonCase):

    def setUp(self, *args, **kwargs):
        super(AnonymousItemCase, self).setUp(*args, **kwargs)
        self.partner = self.env.ref('shoptor.anonymous')
        self.cart = self.env.ref('shoptor.sale_order_1')
        self.cart_id = self.cart.id
        self.service = self._get_service(CartItemService, None)
        self.cart_service = self._get_service(CartService, None)


class ConnectedItemCase(AbstractItemCase, CommonCase):

    def setUp(self, *args, **kwargs):
        super(ConnectedItemCase, self).setUp(*args, **kwargs)
        self.partner = self.env.ref('shoptor.partner_1')
        self.cart = self.env.ref('shoptor.sale_order_2')
        self.cart_id = self.cart.id
        self.service = self._get_service(CartItemService, self.partner)
        self.cart_service = self._get_service(CartService, self.partner)
