# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader.tests.common import ProductCommonCase


class ProductBrandCase(ProductCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.brand = cls.env["product.brand"].create({"name": "Foo"})
        cls.lang_en = cls.env.ref("base.lang_en")
        cls.binding = cls.env["shopinvader.brand"].create(
            {
                "backend_id": cls.backend.id,
                "lang_id": cls.lang_en.id,
                "record_id": cls.brand.id,
                "active": True,
            }
        )

    def test_url_key(self):
        binding = self.binding
        self.assertEqual(binding.url_key, "foo")
        self.brand.write({"name": "BAR"})
        binding.refresh()
        self.assertEqual(binding.url_key, "bar")
        self.assertEqual(binding.redirect_url_key, ["foo"])

    def test_inactive(self):
        self.brand.active = False
        self.assertFalse(self.binding.active)

    def test_add_brand(self):
        self.assertFalse(self.shopinvader_variant.shopinvader_brand_id)
        self.template.product_brand_id = self.brand
        self.assertEqual(self.shopinvader_variant.shopinvader_brand_id, self.binding)
