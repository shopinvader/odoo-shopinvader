# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import TestCategoryBindingBase, TestProductBindingBase


class TestProductBinding(TestProductBindingBase):
    def test_serialize(self):
        self.product_binding.recompute_json()
        data = self.product_binding.data
        self.assertEqual(data["id"], self.product.id)
        self.assertEqual(data["model"], {"name": self.product.product_tmpl_id.name})
        self.assertEqual(data["name"], self.product.full_name)
        self.assertEqual(data["short_name"], "blue")
        self.assertEqual(data["variant_count"], 2)
        self.assertEqual(data["sku"], "VORCHAIR-001")
        self.assertEqual(data["variant_attributes"], {"color": "blue"})

    def test_main_variant_index(self):
        variants = self.product.product_tmpl_id.product_variant_ids
        for variant in variants:
            variant._add_to_index(self.se_product_index)
        main_variant = variants.with_context(
            index_id=self.se_product_index.id
        ).filtered("main")
        self.assertEqual(len(main_variant), 1)
        main_variant_binding = main_variant.se_binding_ids[0]
        main_variant_binding.recompute_json()
        self.assertTrue(main_variant_binding.data["main"])

        main_variant.se_binding_ids.unlink()
        main_variant2 = variants.with_context(
            index_id=self.se_product_index.id
        ).filtered("main")
        self.assertEqual(len(main_variant2), 1)
        self.assertNotEqual(main_variant, main_variant2)
        main_variant2_binding = main_variant2.se_binding_ids[0]
        main_variant2_binding.recompute_json()
        self.assertTrue(main_variant2_binding.data["main"])


class TestProductCategBinding(TestProductBindingBase, TestCategoryBindingBase):
    def test_serialize_categories_not_in_index(self):
        self.product_binding.recompute_json()
        self.assertFalse(self.product_binding.data["categories"])

    def test_serialize_categories_in_index(self):
        self.product.categ_id._add_to_index(self.se_categ_index)
        self.product_binding.recompute_json()
        self.assertEqual(len(self.product_binding.data["categories"]), 1)
        category_data = self.product_binding.data["categories"][0]
        self.assertEqual(category_data["id"], self.product.categ_id.id)
        self.assertEqual(category_data["name"], self.product.categ_id.name)
        self.assertEqual(category_data["level"], 0)

    def test_serialize_categories_in_index_other_lang(self):
        self.se_categ_index.lang_id = self.env.ref("base.lang_fr").id
        self.product.categ_id._add_to_index(self.se_categ_index)
        self.product_binding.recompute_json()
        self.assertFalse(self.product_binding.data["categories"])
