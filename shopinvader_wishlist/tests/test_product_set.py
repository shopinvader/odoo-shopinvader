# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
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

    # TODO: disabled for temporary fix to rely only on partner lang.
    # See ../models/product_set.py
    # def test_create_no_variant_switch_lang(self):
    #     lang_fr = self._install_lang("base.lang_fr")
    #     self.backend.lang_ids |= lang_fr
    #     self.prod_set.lang_id = lang_fr
    #     # ensure we can create a line from the product and we get the variant
    #     prod = self.env.ref("product.product_product_4b")
    #     self._bind_products(prod)
    #     line = self.prod_set.set_line_ids.create(
    #         {
    #             "product_set_id": self.prod_set.id,
    #             "product_id": prod.id,
    #             "quantity": 1,
    #         }
    #     )
    #     # test it w/ multi lang
    #     variant_en = prod._get_invader_variant(self.backend, "en_US")
    #     variant_fr = prod._get_invader_variant(self.backend, "fr_FR")
    #     self.assertEqual(line.shopinvader_variant_id, variant_fr)
    #     self.prod_set.lang_id = False
    #     line = self.prod_set.set_line_ids.create(
    #         {
    #             "product_set_id": self.prod_set.id,
    #             "product_id": prod.id,
    #             "quantity": 1,
    #         }
    #     )
    #     self.assertEqual(line.shopinvader_variant_id, variant_en)

    def test_get_lines_by_products(self):
        # ensure we can create a line from the product and we get the variant
        prod = self.env.ref("product.product_product_4d")
        line = self.prod_set.set_line_ids.create(
            {
                "product_set_id": self.prod_set.id,
                "product_id": prod.id,
                "quantity": 1,
            }
        )
        variant = prod.shopinvader_bind_ids[0]
        self.assertEqual(
            self.prod_set.get_lines_by_products(
                invader_variant_ids=variant.ids
            ),
            line,
        )
        self.assertEqual(
            self.prod_set.get_lines_by_products(product_ids=prod.ids), line
        )
        with self.assertRaises(exceptions.ValidationError):
            self.prod_set.get_lines_by_products()

    def test_get_line_by_product_backward_compat(self):
        # ensure old method `get_line_by_product` works
        prod = self.env.ref("product.product_product_4d")
        line = self.prod_set.set_line_ids.create(
            {
                "product_set_id": self.prod_set.id,
                "product_id": prod.id,
                "quantity": 1,
            }
        )
        variant = prod.shopinvader_bind_ids[0]
        self.assertEqual(
            self.prod_set.get_line_by_product(invader_variant_id=variant.id),
            line,
        )
        self.assertEqual(
            self.prod_set.get_line_by_product(product_id=prod.id), line
        )
        with self.assertRaises(exceptions.ValidationError):
            self.prod_set.get_line_by_product()
