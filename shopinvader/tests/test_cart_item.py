# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import CommonCase


class AbstractItemCase(object):

    def setUp(self, *args, **kwargs):
        super(AbstractItemCase, self).setUp(*args, **kwargs)
        self.product_1 = self.env.ref('product.product_product_4b')
        self.product_2 = self.env.ref('product.product_product_13')

    def extract_cart(self, response):
        self.shopinvader_session['cart_id'] =\
            response['set_session']['cart_id']
        self.assertEqual(response['store_cache'], {'cart': response['data']})
        return response['data']

    def add_item(self, product_id, qty):
        return self.extract_cart(
            self.service.dispatch('add_item', params={
                'product_id': product_id,
                'item_qty': qty,
                }))

    def update_item(self, item_id, qty):
        return self.extract_cart(
            self.service.dispatch('update_item', params={
                'item_id': item_id,
                'item_qty': qty,
                }))

    def delete_item(self, item_id):
        return self.extract_cart(
            self.service.dispatch('delete_item', params={
                'item_id': item_id,
                }))

    def check_product_and_qty(self, line, product_id, qty):
        self.assertEqual(line['product']['id'], product_id)
        self.assertEqual(line['qty'], qty)

    def test_add_item_without_cart(self):
        self.remove_cart()
        last_order = self.env['sale.order'].search(
            [], limit=1, order='id desc')
        cart = self.add_item(self.product_1.id, 2)
        self.assertGreater(cart['id'], last_order.id)
        self.assertEqual(len(cart['lines']['items']), 1)
        self.assertEqual(cart['lines']['count'], 2)
        self.check_product_and_qty(
            cart['lines']['items'][0], self.product_1.id, 2)
        self.check_partner(cart)

    def test_add_item_with_an_existing_cart(self):
        cart = self.service.search()['data']
        nbr_line = len(cart['lines']['items'])

        cart = self.add_item(self.product_1.id, 2)
        self.assertEqual(cart['id'], self.cart.id)
        self.assertEqual(len(cart['lines']['items']), nbr_line + 1)
        self.check_product_and_qty(
            cart['lines']['items'][-1], self.product_1.id, 2)
        self.check_partner(cart)

    def test_update_item(self):
        line_id = self.cart.order_line[0].id
        product_id = self.cart.order_line[0].product_id.id
        cart = self.update_item(line_id, 5)
        self.check_product_and_qty(cart['lines']['items'][0], product_id, 5)

    def test_delete_item(self):
        cart = self.service.search()['data']
        items = cart['lines']['items']
        nbr_line = len(items)
        cart = self.delete_item(items[0]['id'])
        self.assertEqual(len(cart['lines']['items']), nbr_line - 1)

    def test_add_item_with_same_product_without_cart(self):
        self.remove_cart()
        cart = self.add_item(self.product_1.id, 1)
        self.assertEqual(len(cart['lines']['items']), 1)
        self.check_product_and_qty(
            cart['lines']['items'][0], self.product_1.id, 1)
        cart = self.add_item(self.product_1.id, 1)
        self.assertEqual(len(cart['lines']['items']), 1)
        self.check_product_and_qty(
            cart['lines']['items'][0], self.product_1.id, 2)

    def remove_cart(self):
        self.cart.unlink()
        self.shopinvader_session.pop('cart_id')


class AnonymousItemCase(AbstractItemCase, CommonCase):

    def setUp(self, *args, **kwargs):
        super(AnonymousItemCase, self).setUp(*args, **kwargs)
        self.partner = self.backend.anonymous_partner_id
        self.cart = self.env.ref('shopinvader.sale_order_1')
        self.cart.order_line._compute_shopinvader_variant()
        self.shopinvader_session = {'cart_id': self.cart.id}
        with self.work_on_services(
                partner=None,
                shopinvader_session=self.shopinvader_session) as work:
            self.service = work.component(usage='cart')

    def check_partner(self, cart):
        self.assertEqual(cart['shipping']['address'], {})
        self.assertEqual(
            cart['invoicing'], {
                'use_specific_address': False,
                'address': {},
            })


class ConnectedItemCase(AbstractItemCase, CommonCase):

    def setUp(self, *args, **kwargs):
        super(ConnectedItemCase, self).setUp(*args, **kwargs)
        self.partner = self.env.ref('shopinvader.partner_1')
        self.cart = self.env.ref('shopinvader.sale_order_2')
        self.cart.order_line._compute_shopinvader_variant()
        self.shopinvader_session = {'cart_id': self.cart.id}
        with self.work_on_services(
                partner=self.partner,
                shopinvader_session=self.shopinvader_session) as work:
            self.service = work.component(usage='cart')

    def check_partner(self, cart):
        self.assertEqual(cart['shipping']['address']['id'], self.partner.id)
        self.assertEqual(
            cart['invoicing'], {
                'use_specific_address': False,
                'address': {},
            })
