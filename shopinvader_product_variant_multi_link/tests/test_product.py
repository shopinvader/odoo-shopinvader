# Copyright (C) 2020 (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product_template_multi_link.tests.test_product import (
    ProductLinkCaseBase,
)


class ProductVariantLinkCaseBase(ProductLinkCaseBase):
    @classmethod
    def _create_links(cls):
        super()._create_links()
        # set non main variants in the links
        cls.link_upselling_1_2.write(
            {
                "left_product_id": cls.variant_1_2.id,
                "right_product_id": cls.variant_2_2.id,
            }
        )
        cls.link_crosselling_1_3.write(
            {
                "left_product_id": cls.variant_1_2.id,
                "right_product_id": cls.variant_3_2.id,
            }
        )
        cls.link_crosselling_2_3.write(
            {
                "left_product_id": cls.variant_2_2.id,
                "right_product_id": cls.variant_3_2.id,
            }
        )
        cls.link_one_way_3_2.write(
            {
                "left_product_id": cls.variant_3_2.id,
                "right_product_id": cls.variant_2_2.id,
            }
        )


class ProductLinkCase(ProductVariantLinkCaseBase):
    def test_links_tmpl1(self):
        # 1st variant from template 1 gets nothing
        expected = {}
        self.assertEqual(self.shopinvader_variant_1_1.product_links, expected)
        # 2nd variant gets links w/ template 2 and 3 variants
        expected = {
            "up_selling": [{"id": self.variant_2_2.id}],
            "cross_selling": [{"id": self.variant_3_2.id}],
        }
        self.assertEqual(self.shopinvader_variant_1_2.product_links, expected)

    def test_links_tmpl2(self):
        # 1st variant from template 2 gets nothing
        expected = {}
        self.assertEqual(self.shopinvader_variant_2_1.product_links, expected)
        # 2nd variant gets links w/ template 2 and 3 variants
        expected = {
            "up_selling": [{"id": self.variant_1_2.id}],
            "cross_selling": [{"id": self.variant_3_2.id}],
        }
        self.assertEqual(self.shopinvader_variant_2_2.product_links, expected)

    def test_links_tmpl3(self):
        # 1st variant from template 3 gets nothing
        expected = {}
        self.assertEqual(self.shopinvader_variant_3_1.product_links, expected)
        # 2nd variant gets links w/ template 1 and 2 variants
        expected = {
            "cross_selling": [
                {"id": self.variant_1_2.id},
                {"id": self.variant_2_2.id},
            ],
            "one_way": [{"id": self.variant_2_2.id}],
        }
        self.assertEqual(self.shopinvader_variant_3_2.product_links, expected)
