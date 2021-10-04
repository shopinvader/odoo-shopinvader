# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_product_brand.tests.common import ProductBrandCommonCase
from odoo.addons.storage_image_product.tests.common import ProductImageCommonCase


class ProductBrandCase(ProductBrandCommonCase, ProductImageCommonCase):
    def test_basic_images_compute(self):
        image_obj = self.env["product.brand.image.relation"]
        image_obj.create({"brand_id": self.brand.id, "image_id": self.logo_image.id})
        image_obj.create({"brand_id": self.brand.id, "image_id": self.black_image.id})
        images = self.binding.images

        self.assertEqual(len(images), 2)
        for image in images:
            for scale in self.backend.shopinvader_brand_resize_ids:
                img = image[scale.key]
                self.assertEqual(img["alt"], self.binding.name)
                self.assertIn(
                    "foo-brand_{0.size_x}_{0.size_y}".format(scale),
                    img["src"],
                )
                self.assertIn("tag", img)
