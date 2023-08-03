# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_v1_base.tests.test_sale import CommonSaleCase


class TestShopinvaderSalePriceUpdate(CommonSaleCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_1 = cls.env.ref("product.product_product_24")
        cls.line = cls.env.ref("shopinvader.sale_order_line_4")
        cls.precision = cls.env["decimal.precision"].precision_get("Product Price")

    def _create_pricelists(self, fixed_price, reduction):
        """
        Create 2 new pricelists (one with a fixed price) and another
        (based on the first) with the given reduction.
        :param fixed_price: float
        :param reduction: float
        :return: bool
        """
        pricelist_values = {
            "name": "Custom pricelist 1",
            "discount_policy": "with_discount",
            "item_ids": [
                (
                    0,
                    0,
                    {
                        "applied_on": "1_product",
                        "product_tmpl_id": self.product_1.product_tmpl_id.id,
                        "compute_price": "fixed",
                        "fixed_price": fixed_price,
                    },
                )
            ],
        }
        self.first_pricelist = self.env["product.pricelist"].create(pricelist_values)
        pricelist_values = {
            "name": "Custom pricelist 2",
            "discount_policy": "with_discount",
            "item_ids": [
                (
                    0,
                    0,
                    {
                        "applied_on": "1_product",
                        "product_tmpl_id": self.product_1.product_tmpl_id.id,
                        "compute_price": "fixed",
                        "fixed_price": fixed_price + reduction,
                    },
                )
            ],
        }
        self.second_pricelist = self.env["product.pricelist"].create(pricelist_values)
        return True

    def test_update_pricelist(self):
        """
        Cases to test:
        - A pricelist is defined on the backend (applied on the SO)
            => Then change the pricelist (check new price applied)
        - No pricelist defined on the backend (so the default comes from partner)
            => Then define a pricelist on the backend (check applied)
        - Pricelist on the backend (applied on SO)
            => Then remove it (check pricelist from partner is applied)
        :return:
        """
        # Let the user to set some discount if necessary
        self.env.ref("product.group_discount_per_so_line").write(
            {"users": [(4, self.env.user.id, False)]}
        )
        fixed_price = 650
        reduction = -100
        self._create_pricelists(fixed_price, reduction)
        self.assertEqual(self.backend.pricelist_id, self.sale.pricelist_id)
        self.backend.write({"pricelist_id": self.first_pricelist.id})
        self.sale._update_pricelist_and_update_line_prices()
        self.assertEqual(self.first_pricelist, self.sale.pricelist_id)
        self.assertAlmostEqual(self.line.price_unit, fixed_price, places=self.precision)
        self.backend.write({"pricelist_id": self.second_pricelist.id})
        self.sale._update_pricelist_and_update_line_prices()
        self.assertEqual(self.second_pricelist, self.sale.pricelist_id)
        self.assertAlmostEqual(
            self.line.price_unit,
            fixed_price + reduction,
            places=self.precision,
        )
