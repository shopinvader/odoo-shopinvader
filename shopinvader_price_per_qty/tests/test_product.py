# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp.addons.shopinvader.tests.common import ProductCommonCase


class ProductCase(ProductCommonCase):

    def test_price(self):
        price_per_qty = {10: 456.52, 20: 391.3, 30: 326.09, 40: 260.87}
        pricelist = self.env.ref('shopinvader.pricelist_1')
        fposition = self.env.ref('shopinvader.fiscal_position_1')
        price = self.shopinvader_variant._get_price(pricelist, fposition)
        self.assertEqual(price_per_qty, price['price_per_qty'])
