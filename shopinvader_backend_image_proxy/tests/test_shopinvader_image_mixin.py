# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.shopinvader.tests.common import ProductCommonCase
from odoo.addons.storage_image_product.tests.common import ProductImageCommonCase


class TestShopinvaderImageMixin(ProductImageCommonCase, ProductCommonCase):
    """
    Tests for shopinvader.image.mixin
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend.write({"image_proxy_url": "http://custom.website.dev"})
        cls.env.ref("base.user_demo").write(
            {
                "groups_id": [
                    (
                        4,
                        cls.env.ref("shopinvader.group_shopinvader_manager").id,
                    )
                ]
            }
        )
        img_relation_obj = cls.env["product.image.relation"]
        product_attr = cls.env.ref("product.product_attribute_value_4")
        cls.logo = img_relation_obj.create(
            {
                "product_tmpl_id": cls.template.id,
                "image_id": cls.logo_image.id,
            }
        )
        cls.image_bk = img_relation_obj.create(
            {
                "product_tmpl_id": cls.template.id,
                "image_id": cls.black_image.id,
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
