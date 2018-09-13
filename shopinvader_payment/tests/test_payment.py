# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase
from odoo.exceptions import UserError


class ShopinvaderPaymentCase(CommonConnectedCartCase):

    def setUp(self, *args, **kwargs):
        super(ShopinvaderPaymentCase, self).setUp(*args, **kwargs)
        self.account_payment_mode = self.env.ref(
            'shopinvader_payment.payment_method_check')
        self.cart.write({'payment_mode_id': self.account_payment_mode.id})

    def test_get_cart_payment_info(self):
        response = self.service.dispatch('search')
        self.assertIn('available_methods', response['data']['payment'])
        self.assertEqual(
            response['data']['payment']['available_methods']['count'],
            len(self.backend.payment_method_ids))

    def test_add_check_payment(self):
        self.assertEqual(self.cart.typology, 'cart')
        self.service.dispatch('add_payment', params={
            'payment_mode': {'id': self.account_payment_mode.id}})
        self.assertEqual(
            self.cart.workflow_process_id,
            self.account_payment_mode.workflow_process_id)
        self.assertEqual(self.cart.typology, 'sale')

    def test_no_check_payment(self):
        self.assertEqual(self.cart.typology, 'cart')
        self.env.ref('shopinvader_payment.shopinvader_payment_check').unlink()
        with self.assertRaises(UserError):
            self.service.dispatch('add_payment', params={
                'payment_mode': {'id': self.account_payment_mode.id}})
        self.assertEqual(self.cart.typology, 'cart')
