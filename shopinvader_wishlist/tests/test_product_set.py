# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tools import mute_logger

from odoo.addons.shopinvader.tests.common import CommonCase


class ProductSet(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(ProductSet, cls).setUpClass()
        cls.prod_set = cls.env.ref("shopinvader_wishlist.wishlist_1")
        cls.prod_set.shopinvader_backend_id = cls.backend

    def test_create_no_variant(self):
        # ensure we can create a line from the product and we get the variant
        prod = self.env.ref("product.product_product_4b")
        line = self.prod_set.set_line_ids.create(
            {
                "product_set_id": self.prod_set.id,
                "product_id": prod.id,
                "quantity": 1,
            }
        )
        variant = prod.shopinvader_bind_ids[0]
        self.assertEqual(line.shopinvader_variant_id, variant)
        self.assertEqual(variant.lang_id.code, "en_US")

    def test_archived_product(self):
        # ensure product archived is visible
        # FIXME: create your own products.
        # Seems `sale` module installation causes
        # some `product`'s demo data to disappear.
        prod = self.env.ref("product.product_product_4c")
        line = self.prod_set.set_line_ids.create(
            {
                "product_set_id": self.prod_set.id,
                "product_id": prod.id,
                "quantity": 1,
            }
        )
        self.assertFalse(self.prod_set.shopinvader_has_line_to_check)
        # Only binding and inactive
        variant = prod.shopinvader_bind_ids[0]
        variant.active = False
        self.prod_set.invalidate_cache(["shopinvader_has_line_to_check"])
        line.invalidate_cache()
        self.assertTrue(self.prod_set.shopinvader_has_line_to_check)
        self.assertEqual(line.shopinvader_variant_id, variant)
        # Add a new active binding -> get this instead
        variant2 = self.env["shopinvader.variant"].create(
            {
                "shopinvader_product_id": variant.shopinvader_product_id.id,
                "record_id": prod.id,
                "active": True,
                "backend_id": self.backend.id,
            }
        )
        self.assertEqual(len(prod.shopinvader_bind_ids), 2)
        self.prod_set.invalidate_cache(["shopinvader_has_line_to_check"])
        line.invalidate_cache()
        self.assertFalse(self.prod_set.shopinvader_has_line_to_check)
        self.assertEqual(line.shopinvader_variant_id, variant2)
        # If all variants are inactive, simply get the 1st one
        variant2.active = False
        self.prod_set.invalidate_cache(["shopinvader_has_line_to_check"])
        line.invalidate_cache()
        self.assertTrue(self.prod_set.shopinvader_has_line_to_check)
        self.assertEqual(line.shopinvader_variant_id, variant)

    @mute_logger("odoo.models.unlink")
    def test_create_no_variant_switch_lang(self):
        lang_fr = self._install_lang("base.lang_fr")
        self.backend.lang_ids |= lang_fr
        self.prod_set.partner_id.lang = lang_fr.code
        # ensure we can create a line from the product and we get the variant
        prod = self.env.ref("product.product_product_4b")
        self._bind_products(prod)
        line = self.prod_set.set_line_ids.create(
            {
                "product_set_id": self.prod_set.id,
                "product_id": prod.id,
                "quantity": 1,
            }
        )
        # test it w/ multi lang
        variant_en = prod._get_invader_variant(self.backend, "en_US")
        variant_fr = prod._get_invader_variant(self.backend, "fr_FR")
        self.assertEqual(
            line.with_context(lang="en_US").shopinvader_variant_id, variant_en
        )
        self.assertEqual(
            line.with_context(lang="fr_FR").shopinvader_variant_id, variant_fr
        )
        # delete variant, fallback to the one matching partner lang
        variant_en.unlink()
        self.assertEqual(
            line.with_context(lang="en_US").shopinvader_variant_id, variant_fr
        )

    def test_get_lines_by_products(self):
        # ensure we can create a line from the product and we get the variant
        prod = self.env.ref("product.product_product_4c")
        line = self.prod_set.set_line_ids.create(
            {
                "product_set_id": self.prod_set.id,
                "product_id": prod.id,
                "quantity": 1,
            }
        )
        variant = prod.shopinvader_bind_ids[0]
        self.assertEqual(
            self.prod_set.get_lines_by_products(invader_variant_ids=variant.ids),
            line,
        )
        self.assertEqual(
            self.prod_set.get_lines_by_products(product_ids=prod.ids), line
        )
        with self.assertRaises(exceptions.ValidationError):
            self.prod_set.get_lines_by_products()
