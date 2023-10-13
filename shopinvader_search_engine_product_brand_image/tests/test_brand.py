# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo.addons.shopinvader_search_engine_image.tests.common import (
    TestSeMultiImageThumbnailCase,
)


class ProductBrandCase(TestSeMultiImageThumbnailCase):
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

    def test_basic_images_compute(self):
        brand = self.brand_binding._contextualize(self.brand_binding)
        data = self.brand_index.model_serializer.serialize(brand.record)
        self.assertIn("images", data)
        self.assertEqual(len(data["images"]), 2)

        # Check the images are sorted by sequence
        first_image = data["images"][0]
        # we have 2 sizes as key
        self.assertEqual(len(first_image), 2)
        self.assertEqual(first_image.keys(), {"small", "medium"})

        # check attributes of the first image
        self.assertEqual(first_image["small"]["sequence"], 1)
        self.assertEqual(first_image["small"]["tag"], "tag1")
        self.assertEqual(first_image["small"]["alt"], self.brand.name)

        self.assertRegex(
            first_image["small"]["src"],
            r"\/web/image\/[0-9]+\/test-brand_5_5.png",
        )
        self.assertRegex(
            first_image["medium"]["src"],
            r"\/web/image\/[0-9]+\/test-brand_10_10.png",
        )
        # check attributes of the second image
        second_image = data["images"][1]
        self.assertEqual(second_image["small"]["sequence"], 2)
        self.assertEqual(second_image["small"]["tag"], "tag2")
        self.assertEqual(second_image["small"]["alt"], self.brand.name)
        self.assertRegex(
            second_image["small"]["src"],
            r"\/web/image\/[0-9]+\/test-brand_5_5.png",
        )
        self.assertRegex(
            second_image["medium"]["src"],
            r"\/web/image\/[0-9]+\/test-brand_10_10.png",
        )

    def test_brand_image_sequence(self):
        # we change the sequence of the images
        self.brand_white_image.sequence = 2
        self.brand_black_image.sequence = 1
        # the order into the images field should be different,
        # the first image should be the black one with the tag "tag2"
        self.backend.image_data_url_strategy = "odoo"
        brand = self.brand_binding._contextualize(self.brand_binding)
        data = self.brand_index.model_serializer.serialize(brand.record)
        self.assertIn("images", data)
        self.assertEqual(len(data["images"]), 2)
        # Check the images are sorted by sequence
        first_image = data["images"][0]
        self.assertEqual(first_image["small"]["sequence"], 1)
        self.assertEqual(first_image["small"]["tag"], "tag2")

        second_image = data["images"][1]
        self.assertEqual(second_image["small"]["sequence"], 2)
        self.assertEqual(second_image["small"]["tag"], "tag1")

        # change sequence again
        self.brand_white_image.sequence = 1
        self.brand_black_image.sequence = 2
        self.brand.invalidate_recordset()
        data = self.brand_index.model_serializer.serialize(brand.record)
        first_image = data["images"][0]
        self.assertEqual(first_image["small"]["sequence"], 1)
        self.assertEqual(first_image["small"]["tag"], "tag1")

        second_image = data["images"][1]
        self.assertEqual(second_image["small"]["sequence"], 2)
        self.assertEqual(second_image["small"]["tag"], "tag2")

    def test_brand_image_src(self):
        self.backend.image_data_url_strategy = "odoo"
        brand = self.brand_binding._contextualize(self.brand_binding)
        data = self.brand_index.model_serializer.serialize(brand.record)
        image = data["images"][0]
        self.assertRegex(
            image["medium"]["src"],
            r"\/web/image\/[0-9]+\/test-brand_10_10.png",
        )

        self.backend.image_data_url_strategy = "storage_url"
        data = self.brand_index.model_serializer.serialize(brand.record)
        image = data["images"][0]
        self.assertRegex(
            image["medium"]["src"],
            r"https:\/\/media.alcyonbelux.be\/test-brand_10_10-[0-9]+-[0-9]+.png",
        )

        self.backend.image_data_url_strategy = "url_path"
        data = self.brand_index.model_serializer.serialize(brand.record)
        image = data["images"][0]
        self.assertRegex(
            image["medium"]["src"],
            r"\/test-brand_10_10-[0-9]+-[0-9]+.png",
        )
