# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.shopinvader.tests.common import ProductCommonCase
from odoo.addons.storage_image_product.tests.common import (
    ProductImageCommonCase,
)


class TestShopinvaderImageMixin(ProductCommonCase, ProductImageCommonCase):
    """
    Tests for shopinvader.image.mixin
    """

    def setUp(self):
        super(TestShopinvaderImageMixin, self).setUp()
        self.backend.write({"image_proxy_url": "http://custom.website.dev"})
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
        img_relation_obj = self.env["product.image.relation"]
        product_attr = self.env.ref("product.product_attribute_value_4")
        self.logo = img_relation_obj.create(
            {
                "product_tmpl_id": self.template.id,
                "image_id": self.logo_image.id,
            }
        )
        self.image_bk = img_relation_obj.create(
            {
                "product_tmpl_id": self.template.id,
                "image_id": self.black_image.id,
                "attribute_value_ids": [(6, 0, product_attr.ids)],
            }
        )

    def test_image_url(self):
        """
        Ensure the url into images serialized field is correctly updated
        :return:
        """
        image_proxy_url = self.backend.image_proxy_url
        images = self.shopinvader_variant.images
        # Ensure that we have some images for this test
        self.assertTrue(bool(images))
        for image_sizes in images:
            for image_dict in image_sizes.values():
                src = image_dict.get("src")
                self.assertIn(image_proxy_url, src)
