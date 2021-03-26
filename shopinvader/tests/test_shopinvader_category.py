# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from .common import ProductCommonCase


class TestShopinvaderCategory(ProductCommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestShopinvaderCategory, cls).setUpClass()
        cls.shopinvader_categ_obj = cls.env["shopinvader.category"]
        cls.product_category = cls.env.ref("product.product_category_4")
        cls.categ_parent = cls.product_category.parent_id
        cls.lang = cls.env["res.lang"]._lang_get("en_US")

    def test_real_level1(self):
        """
        Ensure the real_level is correctly computed.
        For this case, the category don't have any parent.
        :return:
        """
        shop_categ = self.shopinvader_categ_obj.create(
            {
                "name": self.product_category.name,
                "lang_id": self.lang.id,
                "backend_id": self.backend.id,
                "record_id": self.product_category.id,
            }
        )
        self.assertEquals("000.000", shop_categ.real_level)
        shop_categ.sequence = 17
        self.assertEquals("000.017", shop_categ.real_level)

    def test_real_level2(self):
        """
        Ensure the real_level is correctly computed.
        For this case, the category have a parent.
        :return:
        """
        self.shopinvader_categ_obj.create(
            {
                "name": self.categ_parent.name,
                "lang_id": self.lang.id,
                "backend_id": self.backend.id,
                "record_id": self.categ_parent.id,
                "sequence": 10,
            }
        )
        shop_categ = self.shopinvader_categ_obj.create(
            {
                "name": self.product_category.name,
                "lang_id": self.lang.id,
                "backend_id": self.backend.id,
                "record_id": self.product_category.id,
                "sequence": 20,
            }
        )
        self.assertEquals("001.010.020", shop_categ.real_level)
        shop_categ.sequence = 30
        self.assertEquals("001.010.030", shop_categ.real_level)
