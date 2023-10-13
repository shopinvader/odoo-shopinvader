# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_search_engine.tests.common import TestBindingIndexBase


class TestBrandBinding(TestBindingIndexBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.brand = cls.env["product.brand"].create({"name": "Test Brand"})
        # create index for brand
        cls.brand_index = cls.env["se.index"].create(
            {
                "name": "brand",
                "backend_id": cls.backend.id,
                "model_id": cls.env.ref("product_brand.model_product_brand").id,
                "serializer_type": "shopinvader_brand_exports",
            }
        )
        cls.brand_binding = cls.brand._add_to_index(cls.brand_index)

    def test_product_brand(self):
        brand = self.brand_binding._contextualize(self.brand_binding)
        data = self.brand_index.model_serializer.serialize(brand.record)
        self.assertIn("name", data)
        self.assertEqual(data["name"], "Test Brand")
