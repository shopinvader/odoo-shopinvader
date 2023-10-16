# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import TestProductBindingUpdateBase


class TestUpdate(TestProductBindingUpdateBase):
    def test_simple_update(self):
        self.product.name = "new name"
        self.assertEqual(self.product_binding.state, "to_recompute")

    def test_update_template(self):
        self.product.product_tmpl_id.name = "new name"
        self.assertEqual(self.product_binding.state, "to_recompute")
