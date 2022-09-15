# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.shopinvader.tests.common import ProductCommonCase
from odoo.addons.storage_image_product.tests.common import ProductImageCommonCase


class TestShopinvaderBackendTest(ProductCommonCase, ProductImageCommonCase):
    """
    Tests for shopinvader.backend
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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

    def _test_url(self, input_val, output, proxy):
        if proxy:
            self.backend.image_proxy_url = proxy
        self.assertEqual(output, self.backend._replace_by_proxy(input_val))

    def test_replace_url(self):
        self._test_url(
            input_val="https://example.com/img.png",
            output="https://test.com/img.png",
            proxy="https://test.com",
        )

    def test_replace_url_with_params(self):
        self._test_url(
            input_val="https://example.com/img.png?foo=bar",
            output="https://test.com/img.png?foo=bar",
            proxy="https://test.com",
        )

    def test_replace_url_with_subdomain(self):
        self._test_url(
            input_val="https://sub.example.com/abc/img.png",
            output="https://test.com/img.png",
            proxy="https://test.com",
        )
        self._test_url(
            input_val="https://example.com/img.png",
            output="https://sub.test.com/abc/img.png",
            proxy="https://sub.test.com/abc",
        )

    def test_replace_url_scheme(self):
        self._test_url(
            input_val="http://example.com/img.png",
            output="https://test.com/img.png",
            proxy="https://test.com",
        )

    def test_do_not_replace_url(self):
        self._test_url(
            input_val="https://example.com/img.png",
            output="https://example.com/img.png",
            proxy=None,
        )
