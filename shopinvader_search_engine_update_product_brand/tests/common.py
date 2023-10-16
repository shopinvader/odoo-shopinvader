# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_search_engine_update.tests.common import (
    TestProductBindingUpdateBase,
)


class TestProductBrandUpdateBase(TestProductBindingUpdateBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.brand = cls.env["product.brand"].create({"name": "brand"})
        cls.brand_index = cls.env["se.index"].create(
            {
                "name": "brand",
                "backend_id": cls.backend.id,
                "model_id": cls.env.ref("product_brand.model_product_brand").id,
                "serializer_type": "shopinvader_brand_exports",
            }
        )
        cls.product.product_brand_id = cls.brand
        cls.brand_binding = cls.brand._add_to_index(cls.brand_index)
        cls.brand_binding.state = "done"
        cls.new_brand = cls.env["product.brand"].create({"name": "new brand"})
        cls.new_brand_binding = cls.new_brand._add_to_index(cls.brand_index)
        cls.new_brand_binding.state = "done"
