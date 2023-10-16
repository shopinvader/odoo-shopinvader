# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import ProductBrandImageCase


class TestBrand(ProductBrandImageCase):
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
