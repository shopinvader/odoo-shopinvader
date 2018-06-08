# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.shopinvader.tests.common import ProductCommonCase


class TestShopinvaderVariant(ProductCommonCase):
    """
    Tests for shopinvader.variant
    """

    def test_price(self):
        """
        Test if price field is correctly computed
        :return: bool
        """
        # Expecting values
        expected_results = {
            'public_tax_exc': {
                'tax_included': False,
                'value': 652.17,
            },
            'public_tax_inc': {
                'tax_included': True,
                'value': 750.0,
            },
            'pro_tax_exc': {
                'tax_included': False,
                'value': 521.74,
            },
            'default': {
                'tax_included': True,
                'value': 750.0,
            },
        }

        computed_price = self.shopinvader_variant.price
        for key, expected_dict in expected_results.items():
            self.assertIn(key, computed_price.keys())
            price_value = computed_price[key]
            for value_key, expected_value in price_value.items():
                self.assertEqual(expected_value, price_value[value_key])
