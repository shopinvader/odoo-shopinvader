# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase


class ShopinvaderPaymentCase(CommonConnectedCartCase):

    def test_get_cart_payment_info(self):
        response = self.service.dispatch('search')
        self.assertIn('available_methods', response['data']['payment'])
        self.assertEqual(
            response['data']['payment']['available_methods']['count'], 2)
