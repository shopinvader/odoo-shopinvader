# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase


class ShopinvaderQuotationPaymentCase(CommonConnectedCartCase):

    def test_get_no_cart_payment_info(self):
        self.cart.order_line[0].product_id.only_quotation = True
        response = self.service.dispatch('search')
        self.assertEqual(
            response['data']['payment']['available_methods']['count'],
            0)
