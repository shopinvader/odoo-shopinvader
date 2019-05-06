# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.shopinvader.tests.common import ProductCommonCase
from odoo.addons.storage_image_product.tests.common import (
    ProductImageCommonCase,
)


class TestShopinvaderBackendTest(ProductCommonCase, ProductImageCommonCase):
    """
    Tests for shopinvader.backend
    """

    def setUp(self):
        super(TestShopinvaderBackendTest, self).setUp()
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

    def _test_url(self, input, output, proxy):
        if proxy:
            self.backend.image_proxy_url = proxy
        self.assertEqual(output, self.backend._replace_by_proxy(input))

    def test_replace_url(self):
        self._test_url(
            input="https://example.com/img.png",
            output="https://test.com/img.png",
            proxy="https://test.com",
        )

    def test_replace_url_with_params(self):
        self._test_url(
            input="https://example.com/img.png?foo=bar",
            output="https://test.com/img.png?foo=bar",
            proxy="https://test.com",
        )

    def test_replace_url_with_subdomain(self):
        self._test_url(
            input="https://sub.example.com/abc/img.png",
            output="https://test.com/img.png",
            proxy="https://test.com",
        )
        self._test_url(
            input="https://example.com/img.png",
            output="https://sub.test.com/abc/img.png",
            proxy="https://sub.test.com/abc",
        )

    def test_replace_url_scheme(self):
        self._test_url(
            input="http://example.com/img.png",
            output="https://test.com/img.png",
            proxy="https://test.com",
        )

    def test_do_not_replace_url(self):
        self._test_url(
            input="https://example.com/img.png",
            output="https://example.com/img.png",
            proxy=None,
        )
