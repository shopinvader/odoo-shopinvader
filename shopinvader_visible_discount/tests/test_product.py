# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader.tests.common import ProductCommonCase


class ProductCase(ProductCommonCase):

    def test_price(self):
        pricelist = self.env.ref('shopinvader.pricelist_1')
        pricelist.visible_discount = True
        fposition = self.env.ref('shopinvader.fiscal_position_1')
        price = self.shopinvader_variant._get_price(pricelist, fposition)
        self.assertEqual(price['discount'], 20)
        self.assertEqual(price['value'], 521.74)
        self.assertEqual(price['original_value'], 652.17)
