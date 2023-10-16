# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64

from odoo.addons.shopinvader_search_engine_image.tests.common import (
    TestSeMultiImageThumbnailCase,
)


class ProductBrandImageCase(TestSeMultiImageThumbnailCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend.image_data_url_strategy = "odoo"
        # create index for brands
        cls.brand_index = cls.env["se.index"].create(
            {
                "name": "brand",
                "backend_id": cls.backend.id,
                "model_id": cls.env.ref("product_brand.model_product_brand").id,
                "serializer_type": "shopinvader_brand_exports",
            }
        )
        # create sizes for brands
        cls.env["se.image.field.thumbnail.size"].create(
            {
                "model_id": cls.env.ref("product_brand.model_product_brand").id,
                "field_id": cls.env.ref(
                    "fs_product_brand_multi_image.field_product_brand__image_ids"
                ).id,
                "backend_id": cls.backend.id,
                "size_ids": [(6, 0, [cls.size_small.id, cls.size_medium.id])],
            }
        )
        cls.brand = cls.env["product.brand"].create(
            {
                "name": "Test Brand",
            }
        )
        cls.brand_white_image = cls.env["fs.product.brand.image"].create(
            {
                "sequence": 1,
                "brand_id": cls.brand.id,
                "specific_image": {
                    "filename": "white.png",
                    "content": base64.b64encode(cls.white_image),
                },
                "tag_id": cls.tag1.id,
            }
        )
        cls.brand_black_image = cls.env["fs.product.brand.image"].create(
            {
                "sequence": 2,
                "brand_id": cls.brand.id,
                "specific_image": {
                    "filename": "black.png",
                    "content": base64.b64encode(cls.black_image),
                },
                "tag_id": cls.tag2.id,
            }
        )
        cls.brand_binding = cls.brand._add_to_index(cls.brand_index)

    def setUp(self):
        super().setUp()
        self.fs_storage = self.env["fs.storage"].create(
            {
                "name": "Temp FS Storage",
                "protocol": "memory",
                "code": "mem_dir_brand",
                "directory_path": "/tmp/",
                "model_xmlids": "fs_product_brand_multi_image.model_fs_product_brand_image",
                "base_url": "https://media.alcyonbelux.be/",
                "is_directory_path_in_url": False,
            }
        )
