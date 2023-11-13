# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from .common import TestSeMultiImageThumbnailCase


class TestShopinvaderSearchEngineImage(TestSeMultiImageThumbnailCase):
    def test_index_no_thumbnail_sizes(self):
        self.backend.image_field_thumbnail_size_ids = None
        product = self.product_binding._contextualize(self.product_binding)
        data = self.product_index.model_serializer.serialize(product.record)
        self.assertEqual(data["images"], [])

    def test_product_image(self):
        self.backend.image_data_url_strategy = "odoo"
        product = self.product_binding._contextualize(self.product_binding)
        data = self.product_index.model_serializer.serialize(product.record)
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
        self.assertEqual(first_image["small"]["alt"], self.product.name)
        self.assertRegex(
            first_image["small"]["src"],
            r"\/web/image\/[0-9]+\/test-product_5_5.png",
        )
        self.assertRegex(
            first_image["medium"]["src"],
            r"\/web/image\/[0-9]+\/test-product_10_10.png",
        )
        # check attributes of the second image
        second_image = data["images"][1]
        self.assertEqual(second_image["small"]["sequence"], 2)
        self.assertEqual(second_image["small"]["tag"], "tag2")
        self.assertEqual(second_image["small"]["alt"], self.product.name)
        self.assertRegex(
            second_image["small"]["src"],
            r"\/web/image\/[0-9]+\/test-product_5_5.png",
        )
        self.assertRegex(
            second_image["medium"]["src"],
            r"\/web/image\/[0-9]+\/test-product_10_10.png",
        )

    def test_product_image_sequence(self):
        # we change the sequence of the images
        self.product_white_image.sequence = 2
        self.product_black_image.sequence = 1
        # the order into the images field should be different,
        # the first image should be the black one with the tag "tag2"
        self.backend.image_data_url_strategy = "odoo"
        product = self.product_binding._contextualize(self.product_binding)
        data = self.product_index.model_serializer.serialize(product.record)
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
        self.product_white_image.sequence = 1
        self.product_black_image.sequence = 2
        data = self.product_index.model_serializer.serialize(product.record)
        first_image = data["images"][0]
        self.assertEqual(first_image["small"]["sequence"], 1)
        self.assertEqual(first_image["small"]["tag"], "tag1")

        second_image = data["images"][1]
        self.assertEqual(second_image["small"]["sequence"], 2)
        self.assertEqual(second_image["small"]["tag"], "tag2")

    def test_product_image_src(self):
        self.backend.image_data_url_strategy = "odoo"
        product = self.product_binding._contextualize(self.product_binding)
        data = self.product_index.model_serializer.serialize(product.record)
        image = data["images"][0]
        self.assertRegex(
            image["medium"]["src"],
            r"\/web/image\/[0-9]+\/test-product_10_10.png",
        )

        self.backend.image_data_url_strategy = "storage_url"
        data = self.product_index.model_serializer.serialize(product.record)
        image = data["images"][0]
        self.assertRegex(
            image["medium"]["src"],
            r"https:\/\/media.alcyonbelux.be\/test-product_10_10-[0-9]+-[0-9]+.png",
        )

        self.backend.image_data_url_strategy = "url_path"
        data = self.product_index.model_serializer.serialize(product.record)
        image = data["images"][0]
        self.assertRegex(
            image["medium"]["src"],
            r"\/test-product_10_10-[0-9]+-[0-9]+.png",
        )
