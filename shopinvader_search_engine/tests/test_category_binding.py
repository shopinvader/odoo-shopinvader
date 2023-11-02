# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import TestCategoryBindingBase


class TestCategoryBinding(TestCategoryBindingBase):
    def _create_parent_category(self):
        parent_category = self.env["product.category"].create(
            {"name": "Parent category"}
        )
        self.category.parent_id = parent_category
        return parent_category

    def test_serialize(self):
        self.category_binding.recompute_json()
        data = self.category_binding.data
        self.assertEqual(data["id"], self.category.id)
        self.assertEqual(data["name"], self.category.name)
        self.assertEqual(data["level"], 0)

    def test_serialize_hierarchy_parent_not_in_index(self):
        self._create_parent_category()
        self.category_binding.recompute_json()
        self.assertFalse(self.category_binding.data["parent"])

    def test_serialize_hierarchy_parent_in_index(self):
        parent_category = self._create_parent_category()
        self.category.invalidate_model()
        parent_binding = parent_category._add_to_index(self.se_index)
        self.category_binding.recompute_json()
        parent_data = self.category_binding.data["parent"]
        self.assertEqual(parent_data["id"], parent_category.id)
        self.assertEqual(parent_data["name"], "Parent category")
        self.assertEqual(parent_data["level"], 0)
        parent_binding.recompute_json()
        self.assertEqual(len(parent_binding.data["childs"]), 1)
        child_data = parent_binding.data["childs"][0]
        self.assertEqual(child_data["id"], self.category.id)
        self.assertEqual(child_data["name"], "Test category")
        self.assertEqual(child_data["level"], 1)
