# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_search_engine.tests.common import TestBindingIndexBase


class TestProductBinding(TestBindingIndexBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.index = cls.env["se.index"].create(
            {
                "name": "product",
                "backend_id": cls.backend.id,
                "model_id": cls.env.ref("product.model_product_product").id,
                "serializer_type": "shopinvader_product_exports",
            }
        )
        cls.product = cls.env.ref("product.product_product_4b")
        cls.product_binding = cls.product._add_to_index(cls.index)

    def test_binding_prices_no_pricelist(self):
        self.product_binding.recompute_json()
        data = self.product_binding.data
        self.assertEqual(len(data["price_by_pricelist"]), 0)

    def test_binding_price_by_pricelist(self):
        pricelist_1 = self.env.ref("product.list0")
        pricelist_2 = self.env.ref("product_get_price_helper.pricelist_1")
        self.index.backend_id.pricelist_ids = [(6, 0, (pricelist_1 | pricelist_2).ids)]
        self.product_binding.recompute_json()
        data = self.product_binding.data
        self.assertEqual(len(data["price_by_pricelist"]), 2)
        self.assertEqual(
            data["price_by_pricelist"][str(pricelist_1.id)],
            {
                "value": 750.0,
                "tax_included": False,
                "discount": 0.0,
                "original_value": 750.0,
            },
        )
        self.assertEqual(
            data["price_by_pricelist"][str(pricelist_2.id)],
            {
                "value": 600.0,
                "tax_included": False,
                "discount": 0.0,
                "original_value": 600.0,
            },
        )
