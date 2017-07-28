# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ..services.cart import CartService
from .common import CommonCase
from ..services.register_anonymous import RegisterAnonymousService
# from openerp.exceptions import Warning as UserError
# from openerp import api, registry


class CartCase(CommonCase):

    def setUp(self):
        super(CartCase, self).setUp()
        self.registry.enter_test_mode()
        self.address = self.env.ref('shopinvader.partner_1_address_1')
        self.fposition = self.env.ref('shopinvader.fiscal_position_2')
        self.default_fposition = self.env.ref('shopinvader.fiscal_position_0')
        templates = self.env['product.template'].search([])
        templates.write({
            'taxes_id': [(6, 0, [self.env.ref('shopinvader.tax_1').id])]})

    def tearDown(self):
        self.registry.leave_test_mode()
        super(CartCase, self).tearDown()


class AnonymousCartCase(CartCase):

    def setUp(self, *args, **kwargs):
        super(AnonymousCartCase, self).setUp(*args, **kwargs)
        self.cart = self.env.ref('shopinvader.sale_order_1')
        self.shopinvader_session = {'cart_id': self.cart.id}
        self.partner = self.backend.anonymous_partner_id
        self.service = self._get_service(CartService, None)
        self.address_ship = {
            'name': 'Purple',
            'street': 'Rue du jardin',
            'zip': '43110',
            'city': 'Aurec sur Loire',
            'phone': '0485485454',
            'country_id': self.env.ref('base.fr').id,
            'email': 'anonymous@customer.example.com',
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
        cart = self.service.update({
            'anonymous_email': self.address_ship.pop('email'),
            'partner_shipping': self.address_ship,
            })
        self._check_address(self.cart.partner_shipping_id, self.address_ship)
        self.assertEqual(cart['data']['use_different_invoice_address'], False)

    def _add_shipping_and_invoice_address(self):
        cart = self.service.update({
            'anonymous_email': self.address_ship.pop('email'),
            'partner_shipping': self.address_ship,
            'partner_invoice': self.address_invoice,
            })
        self._check_address(self.cart.partner_shipping_id, self.address_ship)
        self._check_address(self.cart.partner_invoice_id, self.address_invoice)
        self.assertEqual(cart['data']['use_different_invoice_address'], True)

    def _add_partner(self, partner):
        self.service = self._get_service(CartService, partner)
        self.service.update({
            'assign_partner': True,
            })

    def test_add_new_shipping_address(self):
        cart = self.cart
        self._add_shipping_address()

        self.assertNotEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.partner_id, cart.partner_shipping_id)
        self.assertEqual(cart.partner_id, cart.partner_invoice_id)

    def test_add_new_shipping_address_existing_email(self):
        cart = self.cart
        self.address_ship['email'] = 'osiris@my.personal.address.example.com'
        self.backend.restrict_anonymous = False
        self._add_shipping_address()

        self.assertNotEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.partner_id, cart.partner_shipping_id)
        self.assertEqual(cart.partner_id, cart.partner_invoice_id)

#    def test_add_new_shipping_address_existing_email_fordidden(self):
#        email = 'osiris@my.personal.address.example.com'
#        with self.assertRaises(UserError):
#            with registry(self.env.cr.dbname).cursor() as new_cr:
#                self.env = api.Environment(
#                    new_cr, self.env.uid, self.env.context)
#                self.service = self._get_service(CartService, None)
#                self.service.backend_record.restrict_anonymous = True
#                self.service.update({
#                    'anonymous_email': email,
#                    'partner_shipping': self.address_ship,
#                })
#        self.assertEqual(
#            self.env['sale.order'].browse(self.cart.id).anonymous_email,
#            email)

    def test_add_new_shipping_and_billing_address(self):
        self._add_shipping_and_invoice_address()

        cart = self.cart
        self.assertNotEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.partner_id, cart.partner_shipping_id)
        self.assertNotEqual(cart.partner_id, cart.partner_invoice_id)

    def test_anonymous_cart_then_sign(self):
        cart = self.cart
        partner = self.env.ref('shopinvader.partner_1')
        self._add_partner(partner)
        self.assertEqual(cart.partner_id, partner)
        self.assertEqual(cart.partner_shipping_id, partner)
        self.assertEqual(cart.partner_invoice_id, partner)

    def test_anonymous_cart_then_sign_with_fiscal_position(self):
        cart = self.cart
        partner = self.env.ref('shopinvader.partner_2')
        self._add_partner(partner)
        self.assertEqual(cart.partner_id, partner)
        self.assertEqual(cart.fiscal_position, self.fposition)
        self.assertEqual(cart.amount_total, cart.amount_untaxed)

    def test_anonymous_cart_then_sign_with_pricelist(self):
        cart = self.cart
        self.assertEqual(cart.order_line[0].price_unit, 2950.00)
        self.assertEqual(cart.order_line[1].price_unit, 145.00)
        self.assertEqual(cart.order_line[2].price_unit, 65.00)
        partner = self.env.ref('shopinvader.partner_1')
        pricelist = self.env.ref('shopinvader.pricelist_1')
        partner.property_product_pricelist = pricelist
        self._add_partner(partner)
        self.assertEqual(cart.partner_id, partner)
        self.assertEqual(cart.pricelist_id, pricelist)
        self.assertEqual(cart.order_line[0].price_unit, 2360.00)
        self.assertEqual(cart.order_line[1].price_unit, 116.00)
        self.assertEqual(cart.order_line[2].price_unit, 52.00)

    def test_anonymous_cart_then_create_account(self):
        external_id = "SmUgdmFpcyBldHJlIHBhcGEh"
        self._add_shipping_address()
        self.service.update({
            'next_step': self.backend.last_step_id.code})
        anonymous_service = self._get_service(RegisterAnonymousService, None)
        anonymous_service.create({
            'external_id': external_id,
            'anonymous_token': self.cart.anonymous_token,
            })
        shop_partner = self.cart.partner_id.shopinvader_bind_ids
        self.assertEqual(len(shop_partner), 1)
        self.assertEqual(shop_partner.external_id, external_id)
        self.assertEqual(shop_partner.backend_id, self.backend)


class ConnectedCartCase(CartCase):

    def setUp(self, *args, **kwargs):
        super(ConnectedCartCase, self).setUp(*args, **kwargs)
        self.cart = self.env.ref('shopinvader.sale_order_2')
        self.shopinvader_session = {'cart_id': self.cart.id}
        self.partner = self.env.ref('shopinvader.partner_1')
        self.address = self.env.ref('shopinvader.partner_1_address_1')
        self.service = self._get_service(CartService, self.partner)

    def test_set_shipping_address(self):
        self.service.update({
            'partner_shipping': {'id': self.address.id},
            })
        cart = self.cart
        self.assertEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.partner_shipping_id, self.address)
        self.assertEqual(cart.partner_invoice_id, self.address)

    def test_set_invoice_address(self):
        self.service.update({
            'partner_invoice': {'id': self.address.id},
            })

        cart = self.cart
        self.assertEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.partner_shipping_id, self.partner)
        self.assertEqual(cart.partner_invoice_id, self.address)


class ConnectedCartNoTaxCase(CartCase):

    def setUp(self, *args, **kwargs):
        super(ConnectedCartNoTaxCase, self).setUp(*args, **kwargs)
        self.cart = self.env.ref('shopinvader.sale_order_3')
        self.shopinvader_session = {'cart_id': self.cart.id}
        self.partner = self.env.ref('shopinvader.partner_2')
        self.address = self.env.ref('shopinvader.partner_2_address_1')
        self.service = self._get_service(CartService, self.partner)

    def test_set_shipping_address_with_tax(self):
        cart = self.cart
        self.service.update({
            'partner_shipping': {'id': self.address.id},
            })
        self.assertEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.partner_shipping_id, self.address)
        self.assertEqual(cart.partner_invoice_id, self.address)
        self.assertEqual(cart.fiscal_position, self.default_fposition)
        self.assertNotEqual(cart.amount_total, cart.amount_untaxed)
        self.service.update({
            'partner_shipping': {'id': self.partner.id},
            })
        self.assertEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.partner_shipping_id, self.partner)
        self.assertEqual(cart.partner_invoice_id, self.partner)
        self.assertEqual(cart.fiscal_position, self.fposition)
        self.assertEqual(cart.amount_total, cart.amount_untaxed)

    def test_edit_shipping_address_with_tax(self):
        cart = self.cart
        self.service.update({
            'partner_shipping': {'id': self.address.id},
            })
        self.assertEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.partner_shipping_id, self.address)
        self.assertEqual(cart.partner_invoice_id, self.address)
        self.assertEqual(cart.fiscal_position, self.default_fposition)
        self.assertNotEqual(cart.amount_total, cart.amount_untaxed)

        self.address.write({'country_id': self.env.ref('base.us').id})
        self.assertEqual(cart.partner_id, self.partner)
        self.assertEqual(cart.fiscal_position, self.fposition)
        self.assertEqual(cart.amount_total, cart.amount_untaxed)
