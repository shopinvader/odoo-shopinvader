# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from uuid import uuid4

from odoo.addons.shopinvader_search_engine.tests.test_product_binding import (
    TestProductBinding as BaseTestProductBinding,
)


class TestProductBinding(BaseTestProductBinding):
    """
    Tests for product about seo_title field
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.product.with_context(index_id=cls.se_index.id)

    def test_suffix_empty(self):
        """
        Test when the seo_title_suffix on the backend is empty
        :return:
        """
        self.backend.write({"seo_title_suffix": False})
        # Check default seo_title
        self.assertEqual(self.product.seo_title, "Vortex Side Chair | ")
        # Now check when manual_seo is filled
        title = str(uuid4())
        self.product.write({"seo_title": title})
        self.assertEqual(self.product.seo_title, title)
        self.assertEqual(self.product.manual_seo_title, title)
        # Invalidate cache to ensure data stay in memory
        self.assertEqual(self.product.seo_title, title)

    def test_suffix_normal(self):
        """
        Test when the seo_title_suffix on the backend is filled
        :return:
        """
        self.backend.write({"seo_title_suffix": "Shopinvader Inc."})
        self.assertEqual(self.product.seo_title, "Vortex Side Chair | Shopinvader Inc.")
        # Now check when manual_seo is filled
        title = str(uuid4())
        self.product.write({"seo_title": title})
        self.assertEqual(self.product.seo_title, title)

    def test_suffix_special_char1(self):
        """
        Test when the seo_title_suffix on the backend is filled with some
        special characters
        :return:
        """
        self.backend.write({"seo_title_suffix": "Shopinvader éèiï&|ç{ù$µ"})
        self.assertEqual(
            self.product.seo_title, "Vortex Side Chair | Shopinvader éèiï&|ç{ù$µ"
        )

    def test_suffix_special_char2(self):
        """
        Test when the suffix on the backend is filled with some
        special characters and also the product name
        :return:
        """
        self.backend.write({"seo_title_suffix": "Shopinvader éèiï&|ç{ù$µ"})
        self.product.write({"name": self.product.name + " éèiï&|ç{ù$µ"})
        self.assertEqual(
            self.product.seo_title,
            "Vortex Side Chair éèiï&|ç{ù$µ | Shopinvader éèiï&|ç{ù$µ",
        )
