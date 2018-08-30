# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader.tests.common import ProductCommonCase


class ProductCase(ProductCommonCase):
	"""Enhance the class to check override method."""

    def test_price(self):
        """The method used to test _get_price method."""
        price_per_qty = {10: 456.52, 20: 391.3, 30: 326.09, 40: 260.87}
        pricelist = self.env.ref('shopinvader.pricelist_1')
        fposition = self.env.ref('shopinvader.fiscal_position_1')
        price = self.shopinvader_variant._get_price(pricelist, fposition, None)
        updated_price = {i: round(price['price_per_qty'][i], 2)
                         for i in price['price_per_qty']}
        self.assertEqual(price_per_qty, updated_price)
