# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests.common import TransactionCase

from odoo.addons.extendable.tests.common import ExtendableMixin

from ..schemas.brand import ProductBrand
from ..schemas.product import ProductProduct


class TestProductExpiryInSchema(TransactionCase, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.init_extendable_registry()
        cls.addClassCleanup(cls.reset_extendable_registry)

        cls.lang_id = cls.env["res.lang"]._lang_get_id(cls.env.user.lang)
        cls.brand = cls.env["product.brand"].create(
            {
                "name": "brand",
                "sequence": 1,
                "description": "description",
                "short_description": "short_description",
                "meta_description": "meta_description",
                "meta_keywords": "meta_keywords",
                "seo_title": "seo_title",
                "url_ids": [
                    Command.create(
                        {
                            "key": "url_key",
                            "lang_id": cls.lang_id,
                            "res_model": "product.brand",
                        }
                    ),
                    Command.create(
                        {
                            "key": "redirect_url_key",
                            "lang_id": cls.lang_id,
                            "res_model": "product.brand",
                            "redirect": True,
                        }
                    ),
                ],
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "product", "product_brand_id": cls.brand.id}
        )

    def _test_brand(self, brand):
        self.assertEqual(brand.name, "brand")
        self.assertEqual(brand.sequence, 1)
        self.assertEqual(brand.description, "description")
        self.assertEqual(brand.short_description, "short_description")
        self.assertEqual(brand.meta_description, "meta_description")
        self.assertEqual(brand.meta_keywords, "meta_keywords")
        self.assertEqual(brand.seo_title, "seo_title")
        self.assertEqual(brand.url_key, "url_key")
        self.assertEqual(brand.redirect_url_key, ["redirect_url_key"])

    def test_00(self):
        brand = ProductBrand.from_product_brand(self.brand)
        self._test_brand(brand)

    def test_01(self):
        product = ProductProduct.from_product_product(self.product)
        self._test_brand(product.brand)
