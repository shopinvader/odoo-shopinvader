# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64

from odoo.addons.shopinvader_search_engine.tests.common import TestProductBindingMixin
from odoo.addons.shopinvader_search_engine_product_media.tests.common import (
    ProductMediaCase,
)


class TestUpdate(ProductMediaCase, TestProductBindingMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        TestProductBindingMixin.setup_records(cls)
        cls.env["fs.product.media"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "media_id": cls.media_c.id,
                "sequence": 10,
                "link_existing": True,
            }
        )
        cls.product_binding.state = "done"

    def test_unlink_media(self):
        self.product.media_ids.unlink()
        self.assertEqual(self.product_binding.state, "to_recompute")

    def test_add_media(self):
        self.env["fs.product.media"].create(
            {
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "file": {
                    "filename": "new.txt",
                    "content": base64.b64encode(b"new media"),
                },
                "media_type_id": self.media_type_b.id,
            }
        )
        self.assertEqual(self.product_binding.state, "to_recompute")

    def test_update_media(self):
        self.product.media_ids[0].media_type_id = self.media_type_a.id
        self.assertEqual(self.product_binding.state, "to_recompute")
