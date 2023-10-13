# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import TestBindingIndexBase


class TestProductBinding(TestBindingIndexBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setup_records()

    @classmethod
    def _prepare_index_values(cls, backend=None):
        backend = backend or cls.backend
        return {
            "name": "Product Index",
            "backend_id": backend.id,
            "model_id": cls.env["ir.model"]
            .search([("model", "=", "product.product")], limit=1)
            .id,
            "lang_id": cls.env.ref("base.lang_en").id,
            "serializer_type": "shopinvader_product_exports",
        }

    @classmethod
    def setup_records(cls, backend=None):
        backend = backend or cls.backend
        # create an index for product model
        cls.se_index = cls.se_index_model.create(cls._prepare_index_values(backend))
        # create a binding + product alltogether
        cls.product = cls.env.ref(
            "shopinvader_product.product_product_chair_vortex_white"
        )
        cls.product_binding = cls.product._add_to_index(cls.se_index)
        cls.product_expected = {"id": cls.product.id, "name": cls.product.name}

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
        self.assertEqual(data["price"], {})

    def test_serialize_categories_not_in_index(self):
        self.product_binding.with_context(index=self.se_index).recompute_json()
        self.assertFalse(self.product_binding.data["categories"])

    def test_serialize_categories_in_index(self):
        self.product.categ_id._add_to_index(self.se_index)
        self.product_binding.with_context(index=self.se_index).recompute_json()
        self.assertEqual(len(self.product_binding.data["categories"]), 1)
        category_data = self.product_binding.data["categories"][0]
        self.assertEqual(category_data["id"], self.product.categ_id.id)
        self.assertEqual(category_data["name"], self.product.categ_id.name)
        self.assertEqual(category_data["level"], 0)

    def test_main_variant_index(self):
        variants = self.product.product_tmpl_id.product_variant_ids
        for variant in variants:
            variant._add_to_index(self.se_index)
        main_variant = variants.with_context(index=self.se_index).filtered("main")
        self.assertEqual(len(main_variant), 1)
        main_variant_binding = main_variant.se_binding_ids[0]
        main_variant_binding.with_context(index=self.se_index).recompute_json()
        self.assertTrue(main_variant_binding.data["main"])

        main_variant.se_binding_ids.unlink()
        main_variant2 = variants.with_context(index=self.se_index).filtered("main")
        self.assertEqual(len(main_variant2), 1)
        self.assertNotEqual(main_variant, main_variant2)
        main_variant2_binding = main_variant2.se_binding_ids[0]
        main_variant2_binding.with_context(index=self.se_index).recompute_json()
        self.assertTrue(main_variant2_binding.data["main"])
