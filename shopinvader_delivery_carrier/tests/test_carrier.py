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
        response = self.service.dispatch('apply_delivery_method', params={
            'carrier': {'id': carrier.id},
            })
        self.assertEqual(self.cart.carrier_id.id, carrier.id)
        return response['data']

    def test_available_carriers(self):
        response = self.service.dispatch('get_delivery_methods')
        self.assertEqual(len(response), 2)

    def test_setting_free_carrier(self):
        cart = self._set_carrier(self.free_carrier)
        self.assertEqual(cart['shipping']['amount']['total'], 0)

    def test_setting_poste_carrier(self):
        cart = self._set_carrier(self.poste_carrier)
        # Check shipping amount
        self.assertEqual(cart['shipping']['amount']['total'], 20)
        self.assertEqual(cart['shipping']['amount']['untaxed'], 17.39)
        self.assertEqual(cart['shipping']['amount']['tax'], 2.61)

        # Check items amount
        self.assertEqual(cart['lines']['amount']['total'], 8555.0)
        self.assertEqual(cart['lines']['amount']['untaxed'], 8555.0)
        self.assertEqual(cart['lines']['amount']['tax'], 0)

        # Check total amount
        self.assertEqual(cart['amount']['total'], 8575.0)
        self.assertEqual(cart['amount']['untaxed'], 8572.39)
        self.assertEqual(cart['amount']['tax'], 2.61)
