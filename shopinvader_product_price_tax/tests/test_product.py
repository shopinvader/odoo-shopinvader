# Copyright 2021 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_v1_product.tests.common import ProductCommonCase


class ProductCase(ProductCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, test_queue_job_no_delay=True))
        cls.backend = cls.backend.with_context(test_queue_job_no_delay=True)

    def _assertDictContains(self, source, values, msg=None):
        if msg is None:
            msg = ""
        for key, value in values.items():
            self.assertEqual(source[key], value, f"key='{key}' {msg}")

    def test_product_price(self):
        self._assertDictContains(
            self.shopinvader_variant.price["default"],
            {
                "value_taxed": 750.0,
                "value_untaxed": 652.17,
                "original_value_taxed": 750.0,
                "original_value_untaxed": 652.17,
            },
        )

    def test_product_get_price(self):
        # self.base_pricelist doesn't define a tax mapping. We are tax included
        fiscal_position_fr = self.env.ref("shopinvader_v1_base.fiscal_position_0")
        price = self.shopinvader_variant._get_price(
            pricelist=self.base_pricelist, fposition=fiscal_position_fr
        )
        self._assertDictContains(
            price,
            {
                "value_taxed": 750.0,
                "value_untaxed": 652.17,
                "original_value_taxed": 750.0,
                "original_value_untaxed": 652.17,
            },
        )
        # promotion price list define a discount of 20% on all product
        promotion_price_list = self.env.ref("shopinvader_v1_base.pricelist_1")
        price = self.shopinvader_variant._get_price(
            pricelist=promotion_price_list, fposition=fiscal_position_fr
        )
        self._assertDictContains(
            price,
            {
                "value_taxed": 600.0,
                "value_untaxed": 521.74,
                "original_value_taxed": 600.0,
                "original_value_untaxed": 521.74,
            },
        )
        # use a fiscal position defining a mapping from tax included to tax
        # excluded
        tax_exclude_fiscal_position = self.env.ref(
            "shopinvader_v1_base.fiscal_position_1"
        )
        price = self.shopinvader_variant._get_price(
            pricelist=self.base_pricelist, fposition=tax_exclude_fiscal_position
        )
        self._assertDictContains(
            price,
            {
                "value_taxed": 750.0,
                "value_untaxed": 652.17,
                "original_value_taxed": 750.0,
                "original_value_untaxed": 652.17,
            },
        )
        price = self.shopinvader_variant._get_price(
            pricelist=promotion_price_list, fposition=tax_exclude_fiscal_position
        )
        self._assertDictContains(
            price,
            {
                "value_taxed": 600.0,
                "value_untaxed": 521.74,
                "original_value_taxed": 600.0,
                "original_value_untaxed": 521.74,
            },
        )

    def test_product_get_price_per_qty(self):
        # Define a promotion price for the product with min_qty = 10
        fposition = self.env.ref("shopinvader_v1_base.fiscal_position_0")
        pricelist = self.base_pricelist
        self.env["product.pricelist.item"].create(
            {
                "name": "Discount on Product when Qty >= 10",
                "pricelist_id": pricelist.id,
                "base": "list_price",
                "compute_price": "percentage",
                "percent_price": "20",
                "applied_on": "0_product_variant",
                "product_id": self.shopinvader_variant.record_id.id,
                "min_quantity": 10.0,
            }
        )
        # Case 1 (qty = 1.0). No discount is applied
        price = self.shopinvader_variant._get_price(
            qty=1.0, pricelist=pricelist, fposition=fposition
        )
        self._assertDictContains(
            price,
            {
                "value_taxed": 750.0,
                "value_untaxed": 652.17,
                "original_value_taxed": 750.0,
                "original_value_untaxed": 652.17,
            },
        )
        # Case 2 (qty = 10.0). Discount is applied
        # promotion price list define a discount of 20% on all product
        price = self.shopinvader_variant._get_price(
            qty=10.0, pricelist=pricelist, fposition=fposition
        )
        self._assertDictContains(
            price,
            {
                "value_taxed": 600.0,
                "value_untaxed": 521.74,
                "original_value_taxed": 600.0,
                "original_value_untaxed": 521.74,
            },
        )

    def test_product_get_price_discount_policy(self):
        # Ensure that discount is with 2 digits
        self.env.ref("product.decimal_discount").digits = 2
        # self.base_pricelist doesn't define a tax mapping. We are tax included
        # we modify the discount_policy
        self.base_pricelist.discount_policy = "without_discount"
        fiscal_position_fr = self.env.ref("shopinvader_v1_base.fiscal_position_0")
        price = self.shopinvader_variant._get_price(
            pricelist=self.base_pricelist, fposition=fiscal_position_fr
        )
        self._assertDictContains(
            price,
            {
                "value_taxed": 750.0,
                "value_untaxed": 652.17,
                "original_value_taxed": 750.0,
                "original_value_untaxed": 652.17,
            },
        )
        # promotion price list define a discount of 20% on all product
        # we modify the discount_policy
        promotion_price_list = self.env.ref("shopinvader_v1_base.pricelist_1")
        promotion_price_list.discount_policy = "without_discount"
        price = self.shopinvader_variant._get_price(
            pricelist=promotion_price_list, fposition=fiscal_position_fr
        )
        self._assertDictContains(
            price,
            {
                "value_taxed": 600.0,
                "value_untaxed": 521.74,
                "original_value_taxed": 750.0,
                "original_value_untaxed": 652.17,
            },
        )
        # use the fiscal position defining a mapping from tax included to tax
        # excluded
        # Tax mapping should not impact the computation of the discount and
        # the original value
        tax_exclude_fiscal_position = self.env.ref(
            "shopinvader_v1_base.fiscal_position_1"
        )
        price = self.shopinvader_variant._get_price(
            pricelist=self.base_pricelist, fposition=tax_exclude_fiscal_position
        )
        self._assertDictContains(
            price,
            {
                "value_taxed": 750.0,
                "value_untaxed": 652.17,
                "original_value_taxed": 750.0,
                "original_value_untaxed": 652.17,
            },
        )
        price = self.shopinvader_variant._get_price(
            pricelist=promotion_price_list, fposition=tax_exclude_fiscal_position
        )
        self._assertDictContains(
            price,
            {
                "value_taxed": 600.0,
                "value_untaxed": 521.74,
                "original_value_taxed": 750.0,
                "original_value_untaxed": 652.17,
            },
        )
