# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestShopinvaderImageCase


class TestShopinvaderImage(TestShopinvaderImageCase):
    # TODO: test permission explicitely if needed

    def test_getting_image_for_black_product(self):
        images = self.shopinvader_variant.images
        self.assertEqual(len(images), 2)
        for image in images:
            self.assertIn("small", image)
            self.assertIn("medium", image)
            self.assertIn("large", image)

        # check url key of image that shoul match product name slugified
        for image in self.shopinvader_variant.image_ids.mapped("image_id"):
            # skip the two first thumbnail as there are odoo thumbnail
            for thumbnail in image.thumbnail_ids[2:]:
                self.assertEqual(thumbnail.url_key, "customizable-desk-config")
