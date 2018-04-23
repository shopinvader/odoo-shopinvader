# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.shopinvader.tests.test_product import ProductCommonCase


class Test(ProductCommonCase):

    def test_price_by_qty(self):
        """
        Test if price are corrects
        :return: bool
        """
        expected_result = {
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
        product = self.shopinvader_variant
        company = self.backend.company_id
        for sale_profile in self.backend.sale_profile_ids:
            fposition = sale_profile.fiscal_position_ids
            if len(fposition) > 0:
                fposition = fposition[0]
            result = product._get_price(
                sale_profile.pricelist_id, fposition, company)
            self.assertDictEqual(expected_result[sale_profile.code], result)
        return True
