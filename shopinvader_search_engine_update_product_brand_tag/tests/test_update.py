# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_search_engine_update_product_brand.tests.common import (
    TestProductBrandUpdateBase,
)


class TestUpdate(TestProductBrandUpdateBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tag = cls.env["product.brand.tag"].create(
            {
                "name": "tag",
            }
        )
        cls.new_tag = cls.env["product.brand.tag"].create(
            {
                "name": "new_tag",
            }
        )
        cls.brand.tag_ids = cls.tag
        cls.brand_binding.state = "done"
        cls.product_binding.state = "done"

    def test_unlink_tag(self):
        self.brand.tag_ids.unlink()
        self.assertEqual(self.brand_binding.state, "to_recompute")
        self.assertEqual(self.product_binding.state, "to_recompute")

    def test_add_tag(self):
        self.brand.tag_ids = self.new_tag
        self.assertEqual(self.brand_binding.state, "to_recompute")
        self.assertEqual(self.product_binding.state, "to_recompute")
        self.brand_binding.state = "done"
        self.product_binding.state = "done"
        self.tag.product_brand_ids = self.brand
        self.assertEqual(self.brand_binding.state, "to_recompute")
        self.assertEqual(self.product_binding.state, "to_recompute")

    def test_update_tag(self):
        self.brand.tag_ids[0].name = "new name"
        self.assertEqual(self.brand_binding.state, "to_recompute")
        self.assertEqual(self.product_binding.state, "to_recompute")
