# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp.addons.shopinvader.tests.common import ProductCommonCase


class ProductCase(ProductCommonCase):

    def test_price(self):
        result = {
            'public_tax_exc': {
                'tax_included': False,
                'value': 652.17},
            'public_tax_inc': {
                'tax_included': True,
                'value': 750.0},
            'pro_tax_exc': {
                'tax_included': False,
                'value': 521.74,
            }}
        for role, vals in self.shopinvader_variant.price.items():
            self.assertEqual(
                result[role]['tax_included'], vals['tax_included'])
            self.assertEqual(
                result[role]['value'], vals['value'])
