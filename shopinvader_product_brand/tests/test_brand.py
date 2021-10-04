# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import ProductBrandCommonCase


class ProductBrandCase(ProductBrandCommonCase):
    def test_url_key(self):
        binding = self.binding
        self.assertEqual(binding.url_key, "foo-brand")
        self.brand.write({"name": "BAR Brand"})
        binding.refresh()
        self.assertEqual(binding.url_key, "bar-brand")
        self.assertEqual(binding.redirect_url_key, ["foo-brand"])

    def test_inactive(self):
        self.brand.active = False
        self.assertFalse(self.binding.active)

    def test_add_brand(self):
        self.assertFalse(self.shopinvader_variant.shopinvader_brand_id)
        self.template.product_brand_id = self.brand
        self.assertEqual(self.shopinvader_variant.shopinvader_brand_id, self.binding)
