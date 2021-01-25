# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.shopinvader.tests.common import ProductCommonCase


class TestShopinvaderVariant(ProductCommonCase):
    """
    Tests for shopinvader.variant
    """

    def _check_price(self, computed_price, expected_price):
        for key, expected_value in expected_price.items():
            self.assertIn(key, computed_price.keys())
            price_value = computed_price[key]
            for value_key, expected_value in expected_value.items():
                self.assertEqual(expected_value, price_value[value_key])

    def test_price_with_sale_profile(self):
        """
        Test if price field is correctly computed
        :return: bool
        """
        self.backend.write({"use_sale_profile": True})
        # Expecting values
        expected_price = {
            "public_tax_exc": {"tax_included": False, "value": 652.17},
            "public_tax_inc": {"tax_included": True, "value": 750.0},
            "pro_tax_exc": {"tax_included": False, "value": 521.74},
        }
        computed_price = self.shopinvader_variant.price
        self._check_price(computed_price, expected_price)

    def test_price_without_sale_profile(self):
        """
        Test if price field is correctly computed
        :return: bool
        """
        # Expecting values
        expected_price = {"default": {"tax_included": True, "value": 750.0}}
        computed_price = self.shopinvader_variant.price
        self._check_price(computed_price, expected_price)
