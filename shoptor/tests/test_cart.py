# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ..services.cart import CartService
from .common import CommonCase


class AbstractCartCase(object):

    def set_up(self):
        self.contact = self.env.ref('shoptor.partner_1_contact_1')
        self.address_ship = {
            'name': 'Purple',
            'street': 'Rue du jardin',
            'zip': '43110',
            'city': 'Aurec sur Loire',
            'phone': '0485485454',
            'country_id': self.env.ref('base.fr').id,
            }
        self.address_invoice = {
            'name': 'Gospel',
            'street': 'Rue du jardin',
            'zip': '43110',
            'city': 'Aurec sur Loire',
            'phone': '0485485454',
            'country_id': self.env.ref('base.fr').id,
            }

    def _check_address(self, partner, data):
        for key in data:
            if key == 'country_id':
                self.assertEqual(partner[key].id, data[key])
            else:
                self.assertEqual(partner[key], data[key])

    def _add_shipping_address(self):
        self.service.update({
            'cart_id': self.cart.id,
            'partner_shipping_id': self.address_ship,
            })
        self._check_address(self.cart.partner_shipping_id, self.address_ship)

    def _add_shipping_and_invoice_address(self):
        self.service.update({
            'cart_id': self.cart.id,
            'partner_shipping_id': self.address_ship,
            'partner_invoice_id': self.address_invoice,
            'use_different_invoice_address': True
            })
        self._check_address(self.cart.partner_shipping_id, self.address_ship)
        self._check_address(self.cart.partner_invoice_id, self.address_invoice)


class AnonymousCartCase(AbstractCartCase, CommonCase):

    def setUp(self, *args, **kwargs):
        super(AnonymousCartCase, self).setUp(*args, **kwargs)
        self.set_up()
        self.cart = self.env.ref('shoptor.sale_order_1')
        self.partner = self.env.ref('shoptor.anonymous')
        self.service = self._get_service(CartService, None)

    def test_add_new_shipping_contact(self):
        cart = self.cart
        self._add_shipping_address()

        self.assertNotEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.partner_id, cart.partner_shipping_id)
        self.assertEqual(cart.partner_id, cart.partner_invoice_id)

    def test_add_new_shipping_and_billing_contact(self):
        self._add_shipping_and_invoice_address()

        cart = self.cart
        self.assertNotEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.partner_id, cart.partner_shipping_id)
        self.assertNotEqual(cart.partner_id, cart.partner_invoice_id)

    def test_anonymous_cart_then_sign(self):
        cart = self.cart
        logged_partner = self.env.ref('shoptor.partner_1')
        self.service.update({
            'cart_id': cart.id,
            'partner_email': logged_partner.email,
            })
        self.assertEqual(cart.partner_id, logged_partner)
        self.assertEqual(cart.partner_shipping_id, self.partner)
        self.assertEqual(cart.partner_invoice_id, self.partner)


class ConnectedCartCase(AbstractCartCase, CommonCase):

    def setUp(self, *args, **kwargs):
        super(ConnectedCartCase, self).setUp(*args, **kwargs)
        self.set_up()
        self.cart = self.env.ref('shoptor.sale_order_2')
        self.partner = self.env.ref('shoptor.partner_1')
        self.partner_email = self.partner.email
        self.contact = self.env.ref('shoptor.partner_1_contact_1')
        self.service = self._get_service(CartService, self.partner)

    def test_add_new_shipping_contact(self):
        self._add_shipping_address()

        cart = self.cart
        self.assertEqual(cart.partner_id, self.partner)
        self.assertNotEqual(cart.partner_shipping_id, self.partner)
        self.assertNotEqual(cart.partner_shipping_id, self.contact)
        self.assertEqual(cart.partner_shipping_id.parent_id, self.partner)
        self.assertEqual(cart.partner_invoice_id, cart.partner_shipping_id)

    def test_set_shipping_contact(self):
        self.address_ship = {'id': self.contact.id}
        self._add_shipping_address()
        self.assertEqual(self.partner, self.contact.parent_id)

        cart = self.cart
        self.assertEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.partner_shipping_id, self.contact)
        self.assertEqual(cart.partner_invoice_id, self.contact)

    def test_add_new_shipping_and_billing_contact(self):
        self._add_shipping_and_invoice_address()

        cart = self.cart
        self.assertEqual(cart.partner_id, self.partner)

        self.assertNotEqual(cart.partner_shipping_id, self.partner)
        self.assertNotEqual(cart.partner_shipping_id, self.contact)
        self.assertEqual(cart.partner_shipping_id.parent_id, self.partner)

        self.assertNotEqual(cart.partner_invoice_id, self.contact)
        self.assertNotEqual(cart.partner_invoice_id, self.partner)
        self.assertEqual(cart.partner_invoice_id.parent_id, self.partner)
