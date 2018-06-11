# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase


class CarrierCase(CommonConnectedCartCase):

    def setUp(self):
        super(CarrierCase, self).setUp()
        self.free_carrier = self.env.ref('delivery.free_delivery_carrier')
        self.poste_carrier = self.env.ref('delivery.delivery_carrier')

    def _set_carrier(self, carrier):
        response = self.service.dispatch('add_carrier', params={
            'carrier': {'id': carrier.id},
            })
        self.assertEqual(self.cart.carrier_id.id, carrier.id)
        return response['data']['shipping']

    def test_available_carriers(self):
        response = self.service.dispatch('search')
        self.assertIn('available_carriers', response['data']['shipping'])
        shipping = response['data']['shipping']
        self.assertEqual(shipping['available_carriers']['count'], 2)

    def test_setting_free_carrier(self):
        shipping = self._set_carrier(self.free_carrier)
        self.assertEqual(shipping['amount']['total'], 0)

    def test_setting_poste_carrier(self):
        shipping = self._set_carrier(self.poste_carrier)
        self.assertEqual(shipping['amount']['total'], 20)
        self.assertEqual(shipping['amount']['untaxed'], 17.39)
        self.assertEqual(shipping['amount']['tax'], 2.61)

    def test_should_only_return_matching_carrier(self):
        # change country to make first carrier method not available
        self.free_carrier.write({
            'country_ids': [(6, 0, self.env.ref('base.us').ids)],
            })
        response = self.service.dispatch('update', params={
            'step': {'current': 'cart_address'},
        })
        # shipping information should be available now
        shipping = response['data']['shipping']
        self.assertEqual(shipping['available_carriers']['count'], 1)

    def test_update_cart_update_price(self):
        self.env.ref('product.product_product_24').weight = 4
        shipping = self._set_carrier(self.poste_carrier)
        self.assertEqual(shipping['amount']['total'], 50)
        self.assertEqual(shipping['amount']['untaxed'], 43.48)
        self.assertEqual(shipping['amount']['tax'], 6.52)

        response = self.service.dispatch('update_item', params={
            'item_id': self.env.ref('shopinvader.sale_order_line_4').id,
            'item_qty': 1,
        })
        shipping = response['data']['shipping']
        self.assertEqual(shipping['amount']['total'], 20)
        self.assertEqual(shipping['amount']['untaxed'], 17.39)
        self.assertEqual(shipping['amount']['tax'], 2.61)

    def test_setting_address_set_default_carrier(self):
        response = self.service.dispatch('update', params={
            'shipping': {'address': {'id': self.address.id}},
        })
        shipping = response['data']['shipping']
        self.assertEqual(
            shipping['selected_carrier']['id'], self.free_carrier.id)

    def test_changing_with_compatible_address_keep_carrier(self):
        self._set_carrier(self.poste_carrier)
        response = self.service.dispatch('update', params={
            'shipping': {'address': {'id': self.address.id}},
        })
        shipping = response['data']['shipping']
        self.assertEqual(
            shipping['selected_carrier']['id'], self.poste_carrier.id)

    def test_changing_with_incompatible_address_change_carrier(self):
        self.free_carrier.write({
            'country_ids': [(6, 0, self.env.ref('base.fr').ids)],
            })
        response = self.service.dispatch('update', params={
            'shipping': {
                'address': {
                    'id': self.env.ref('shopinvader.partner_1_address_2').id
                    }
                },
            })
        shipping = response['data']['shipping']
        self.assertEqual(
            shipping['selected_carrier']['id'], self.poste_carrier.id)
