# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import TestProductBrandUpdateBase


class TestUpdate(TestProductBrandUpdateBase):
    def test_update_brand_update_product(self):
        self.product.product_brand_id.name = "new brand name"
        self.assertEqual(self.product_binding.state, "to_recompute")

    def test_update_brand_update_brand_binding(self):
        self.brand.name = "new brand name"
        self.assertEqual(self.brand_binding.state, "to_recompute")
        # the product is also marked to recompute
        self.assertEqual(self.product_binding.state, "to_recompute")

    def test_update_brand_field_on_product_update_product(self):
        self.product.product_brand_id = self.new_brand
        self.assertEqual(self.product_binding.state, "to_recompute")
