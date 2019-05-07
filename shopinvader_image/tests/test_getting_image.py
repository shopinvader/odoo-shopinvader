# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader.tests.common import ProductCommonCase
from odoo.addons.storage_image_product.tests.common import (
    ProductImageCommonCase,
)


class ShopinvaderImageCase(ProductCommonCase, ProductImageCommonCase):
    def setUp(self):
        super(ShopinvaderImageCase, self).setUp()
        self.env.ref("base.user_demo").write(
            {
                "groups_id": [
                    (
                        4,
                        self.env.ref(
                            "shopinvader.group_shopinvader_manager"
                        ).id,
                    )
                ]
            }
        )
        ProductImageCommonCase.setUp(self)
        self.logo = self.env["product.image.relation"].create(
            {
                "product_tmpl_id": self.template.id,
                "image_id": self.logo_image.id,
            }
        )
        self.image_bk = self.env["product.image.relation"].create(
            {
                "product_tmpl_id": self.template.id,
                "image_id": self.black_image.id,
                "attribute_value_ids": [
                    (
                        6,
                        0,
                        [self.env.ref("product.product_attribute_value_4").id],
                    )
                ],
            }
        )

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
                self.assertEqual(thumbnail.url_key, "ipad-retina-display")
