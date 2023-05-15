# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from datetime import datetime, timedelta

from openerp.addons.shopinvader.tests.common import ProductCommonCase


class ProductCase(ProductCommonCase):
    def test_price(self):
        price_per_qty = {10.0: 456.52, 20.0: 391.3, 30.0: 326.09, 40.0: 260.87}
        pricelist = self.env.ref("shopinvader.pricelist_1")
        fposition = self.env.ref("shopinvader.fiscal_position_1")
        price = self.shopinvader_variant._get_price(
            pricelist=pricelist, fposition=fposition
        )
        self.assertEqual(price_per_qty, price["per_qty"])

    def _test_price_for_case(self, start, end, expected):
        item = self.env.ref("shopinvader_price_per_qty.item_10_discount_30")
        item.update(
            {
                "date_start": start,
                "date_end": end,
            }
        )
        pricelist = self.env.ref("shopinvader.pricelist_1")
        fposition = self.env.ref("shopinvader.fiscal_position_1")
        price = self.shopinvader_variant._get_price(
            pricelist=pricelist, fposition=fposition
        )
        if expected is None:
            self.assertNotIn(10, price["per_qty"])
        else:
            self.assertIn(10, price["per_qty"])
            self.assertEqual(expected, price["per_qty"][10])

    def test_price_with_date(self):
        yesterday = datetime.now() - timedelta(1)
        tomorrow = datetime.now() + timedelta(1)
        self._test_price_for_case(None, None, 456.52)
        self._test_price_for_case(yesterday, None, 456.52)
        self._test_price_for_case(None, tomorrow, 456.52)
        self._test_price_for_case(yesterday, tomorrow, 456.52)

        self._test_price_for_case(None, yesterday, None)
        self._test_price_for_case(tomorrow, None, None)
