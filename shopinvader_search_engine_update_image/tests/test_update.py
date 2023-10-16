# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64

from odoo.addons.shopinvader_search_engine_image.tests.common import (
    TestSeMultiImageThumbnailCase,
)


class TestUpdate(TestSeMultiImageThumbnailCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_binding.state = "done"
        cls.new_tag = cls.env["image.tag"].create(
            {
                "name": "new_tag",
            }
        )

    def test_unlink_image(self):
        self.product.variant_image_ids.unlink()
        self.assertEqual(self.product_binding.state, "to_recompute")

    def test_add_image(self):
        self.env["fs.product.image"].create(
            {
                "sequence": 1,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "specific_image": {
                    "filename": "white2.png",
                    "content": base64.b64encode(self.white_image),
                },
            }
        )
        self.assertEqual(self.product_binding.state, "to_recompute")

    def test_update_image(self):
        self.product.variant_image_ids[0].tag_id = self.new_tag
        self.assertEqual(self.product_binding.state, "to_recompute")
