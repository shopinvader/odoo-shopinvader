# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from uuid import uuid4

from odoo.tools import mute_logger

from .common import ProductCommonCase


@mute_logger("odoo.models.unlink")
class TestShopinvaderVariantTest(ProductCommonCase):
    """
    Tests for shopinvader.variant about seo_title field
    """

    def _check_expected_seo_name(self, backend, variants):
        """
        Check expected result of _build_seo_title
        :param backend: shopinvader.backend
        :param variants: shopinvader.variant
        :return:
        """
        for variant in variants:
            if variant.manual_seo_title:
                result = variant.seo_title
                expected_result = variant.manual_seo_title
            else:
                result = variant._build_seo_title()
                expected_result = u"{} | {}".format(
                    variant.name, backend.website_public_name or u""
                )
            self.assertEquals(result, expected_result)

    def test_public_name_empty(self):
        """
        Test when the website_public_name on the backend is empty
        :return:
        """
        self.backend.write({"website_public_name": False})
        # Check default seo_title
        self._check_expected_seo_name(self.backend, self.shopinvader_variants)
        # Now check when manual_seo is filled
        for variant in self.shopinvader_variants:
            title = str(uuid4())
            variant.write({"seo_title": title})
            self.assertEquals(variant.seo_title, title)
            self.assertEquals(variant.manual_seo_title, title)
        # Invalidate cache to ensure data stay in memory
        self.shopinvader_variants.invalidate_cache()
        self._check_expected_seo_name(self.backend, self.shopinvader_variants)

    def test_public_name_normal(self):
        """
        Test when the website_public_name on the backend is filled
        :return:
        """
        self.backend.write({"website_public_name": "Shopinvader Inc."})
        self._check_expected_seo_name(self.backend, self.shopinvader_variants)
        # Now check when manual_seo is filled
        for variant in self.shopinvader_variants:
            variant.write({"seo_title": str(uuid4())})
        self._check_expected_seo_name(self.backend, self.shopinvader_variants)

    def test_public_name_special_char1(self):
        """
        Test when the website_public_name on the backend is filled with some
        special characters
        :return:
        """
        self.backend.write({"website_public_name": "Shopinvader éèiï&|ç{ù$µ"})
        self._check_expected_seo_name(self.backend, self.shopinvader_variants)

    def test_public_name_special_char2(self):
        """
        Test when the website_public_name on the backend is filled with some
        special characters and also variants
        :return:
        """
        self.backend.write({"website_public_name": "Shopinvader éèiï&|ç{ù$µ"})
        for variant in self.shopinvader_variants:
            variant.write({"name": variant.name + u" éèiï&|ç{ù$µ"})
        self._check_expected_seo_name(self.backend, self.shopinvader_variants)
