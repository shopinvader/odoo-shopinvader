# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
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
        result = {
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
        }
        for sale_profile, values in self.shopinvader_variant.price.items():
            result_profile = result.get(sale_profile, {})
            profile_tax_included = result_profile.get('tax_included', 't')
            profile_value = result_profile.get('value', 't')
            self.assertEqual(profile_tax_included, values.get(
                'tax_included', 0))
            self.assertEqual(profile_value, values.get('value', 0))
        return True
