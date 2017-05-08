# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ..services.cart import CartService
from .common import CommonCase


class AbstractCartCase(object):

    def set_up(self):
        self.contact = self.env.ref('shopinvader.partner_1_contact_1')
        self.fposition = self.env.ref('shopinvader.fiscal_position_2')
        self.default_fposition = self.env.ref('shopinvader.fiscal_position_0')
        templates = self.env['product.template'].search([])
        templates.write({
            'taxes_id': [(6, 0, [self.env.ref('shopinvader.tax_1').id])]})


class AnonymousCartCase(AbstractCartCase, CommonCase):

    def setUp(self, *args, **kwargs):
        super(AnonymousCartCase, self).setUp(*args, **kwargs)
        self.set_up()
        self.cart = self.env.ref('shopinvader.sale_order_1')
        self.shopinvader_session = {'cart_id': self.cart.id}
        self.partner = self.env.ref('shopinvader.anonymous')
        self.service = self._get_service(CartService, None)
        self.address_ship = {
            'name': 'Purple',
            'street': 'Rue du jardin',
            'zip': '43110',
            'city': 'Aurec sur Loire',
            'phone': '0485485454',
            'country_id': self.env.ref('base.fr').id,
            'email': 'anonymous@customer.example.com',
            'external_id': 'WW5KaGRtOD0=',
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
            if key == 'external_id':
                continue
            elif key == 'country_id':
                self.assertEqual(partner[key].id, data[key])
            else:
                self.assertEqual(partner[key], data[key])

    def _add_shipping_address(self):
        self.service.update({
            'partner_shipping_id': self.address_ship,
            })
        self._check_address(self.cart.partner_shipping_id, self.address_ship)

    def _add_shipping_and_invoice_address(self):
        self.service.update({
            'partner_shipping_id': self.address_ship,
            'partner_invoice_id': self.address_invoice,
            'use_different_invoice_address': True
            })
        self._check_address(self.cart.partner_shipping_id, self.address_ship)
        self._check_address(self.cart.partner_invoice_id, self.address_invoice)

    def _add_partner(self, partner):
        self.service = self._get_service(CartService, partner)
        self.service.update({
            'assign_partner': True,
            })

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
        partner = self.env.ref('shopinvader.partner_1')
        addr = partner.address_get(['delivery', 'invoice', 'contact'])
        self._add_partner(partner)
        self.assertEqual(cart.partner_id, partner)
        self.assertEqual(cart.partner_shipping_id.id, addr['delivery'])
        self.assertEqual(cart.partner_invoice_id.id, addr['invoice'])

    def test_anonymous_cart_then_sign_with_fiscal_position(self):
        cart = self.cart
        partner = self.env.ref('shopinvader.partner_2')
        self._add_partner(partner)
        self.assertEqual(cart.partner_id, partner)
        self.assertEqual(cart.fiscal_position, self.fposition)
        self.assertEqual(cart.amount_total, cart.amount_untaxed)

    def test_anonymous_cart_then_sign_with_pricelist(self):
        cart = self.cart
        partner = self.env.ref('shopinvader.partner_1')
        pricelist = self.env.ref('shopinvader.pricelist_1')
        self.assertEqual(cart.order_line[0].price_unit, 2950.00)
        self.assertEqual(cart.order_line[1].price_unit, 145.00)
        self.assertEqual(cart.order_line[2].price_unit, 65.00)
        self._add_partner(partner)
        self.assertEqual(cart.partner_id, partner)
        self.assertEqual(cart.pricelist_id, pricelist)
        self.assertEqual(cart.order_line[0].price_unit, 2360.00)
        self.assertEqual(cart.order_line[1].price_unit, 116.00)
        self.assertEqual(cart.order_line[2].price_unit, 52.00)


class ConnectedCartCase(AbstractCartCase, CommonCase):

    def setUp(self, *args, **kwargs):
        super(ConnectedCartCase, self).setUp(*args, **kwargs)
        self.set_up()
        self.cart = self.env.ref('shopinvader.sale_order_2')
        self.shopinvader_session = {'cart_id': self.cart.id}
        self.partner = self.env.ref('shopinvader.partner_1')
        self.contact = self.env.ref('shopinvader.partner_1_contact_1')
        self.service = self._get_service(CartService, self.partner)

    def test_set_shipping_contact(self):
        self.service.update({
            'partner_shipping_id': self.contact.id,
            })
        cart = self.cart
        self.assertEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.partner_shipping_id, self.contact)
        self.assertEqual(cart.partner_invoice_id, self.contact)

    def test_set_invoice_contact(self):
        self.service.update({
            'use_different_invoice_address': True,
            'partner_invoice_id': self.contact.id,
            })

        cart = self.cart
        self.assertEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.partner_shipping_id, self.partner)
        self.assertEqual(cart.partner_invoice_id, self.contact)


class ConnectedCartNoTaxCase(AbstractCartCase, CommonCase):

    def setUp(self, *args, **kwargs):
        super(ConnectedCartNoTaxCase, self).setUp(*args, **kwargs)
        self.set_up()
        self.cart = self.env.ref('shopinvader.sale_order_3')
        self.shopinvader_session = {'cart_id': self.cart.id}
        self.partner = self.env.ref('shopinvader.partner_2')
        self.contact = self.env.ref('shopinvader.partner_2_contact_1')
        self.service = self._get_service(CartService, self.partner)

    def test_set_shipping_contact_with_tax(self):
        cart = self.cart
        self.service.update({
            'partner_shipping_id': self.contact.id,
            })
        self.assertEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.partner_shipping_id, self.contact)
        self.assertEqual(cart.partner_invoice_id, self.contact)
        self.assertEqual(cart.fiscal_position, self.default_fposition)
        self.assertNotEqual(cart.amount_total, cart.amount_untaxed)
        self.service.update({
            'partner_shipping_id': self.partner.id,
            })
        self.assertEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.partner_shipping_id, self.partner)
        self.assertEqual(cart.partner_invoice_id, self.partner)
        self.assertEqual(cart.fiscal_position, self.fposition)
        self.assertEqual(cart.amount_total, cart.amount_untaxed)
