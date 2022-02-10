# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from unittest import mock

from odoo.addons.shopinvader_image.tests.common import TestShopinvaderImageCase


class TestShopinvaderImageWebpCase(TestShopinvaderImageCase):
    def test_basic_images_compute(self):
        images = self.shopinvader_variant.images_webp
        self.assertEqual(len(images), 2)
        for image in images:
            for scale in self.backend.shopinvader_variant_resize_ids:
                img = image[scale.key]
                self.assertEqual(img["alt"], self.shopinvader_variant.name)
                self.assertIn(
                    "customizable-desk-config-webp_{0.size_x}_{0.size_y}".format(
                        scale
                    ),
                    img["src"],
                )
                self.assertIn("tag", img)

    def test_images_recompute(self):
        variant = self.shopinvader_variant
        with mock.patch.object(
            type(variant), "_get_image_webp_data_for_record"
        ) as mocked:
            mocked.return_value = [{"a": 1, "b": 2}]
            self.assertEqual(variant.images_webp, [{"a": 1, "b": 2}])
            mocked.assert_called()

        variant.invalidate_cache(["images_webp"])
        with mock.patch.object(
            type(variant), "_get_image_webp_data_for_record"
        ) as mocked:
            mocked.return_value = [{"c": 3, "d": 4}]
            # same value as before
            self.assertEqual(variant.images_webp, [{"a": 1, "b": 2}])
            mocked.assert_not_called()

        # simulate change in image scale
        self.backend.shopinvader_variant_resize_ids[0].key = "very-small"
        variant.invalidate_cache(["images_webp"])
        with mock.patch.object(
            type(variant), "_get_image_webp_data_for_record"
        ) as mocked:
            mocked.return_value = [{"c": 3, "d": 4}]
            # recomputed
            self.assertEqual(variant.images_webp, [{"c": 3, "d": 4}])
            mocked.assert_called()
