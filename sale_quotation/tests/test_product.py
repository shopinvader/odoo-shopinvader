# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestProduct(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.attribute = cls.env.ref("product.product_attribute_2")
        cls.value_1 = cls.env.ref("product.product_attribute_value_3")
        cls.value_2 = cls.env.ref("product.product_attribute_value_4")
        cls.product_template = cls.env["product.template"].create(
            {
                "name": "Test Product",
            }
        )

    def test_simple_product(self):
        # Back and forth flow, setting and reading on template and single variant
        self.assertEqual(self.product_template.shop_only_quotation, "never")
        self.product_template.shop_only_quotation = "all_variant"
        self.assertTrue(self.product_template.product_variant_ids.shop_only_quotation)
        self.product_template.product_variant_ids.shop_only_quotation = False
        self.assertEqual(self.product_template.shop_only_quotation, "never")

    def test_multi_product(self):
        # Configure product with multiple variants
        self.product_template.attribute_line_ids = [
            (
                0,
                0,
                {
                    "attribute_id": self.attribute.id,
                    "value_ids": [(6, 0, [self.value_1.id, self.value_2.id])],
                },
            )
        ]
        self.assertEqual(len(self.product_template.product_variant_ids), 2)
        template = self.product_template
        product_1 = self.product_template.product_variant_ids[0]
        product_2 = self.product_template.product_variant_ids[1]
        # Set on the template should set all variants
        template.shop_only_quotation = "all_variant"
        self.assertTrue(product_1.shop_only_quotation)
        self.assertTrue(product_2.shop_only_quotation)
        # Set a variant to false should set the template to false
        # It's only true if it's true for all variants
        product_1.shop_only_quotation = False
        self.assertEqual(template.shop_only_quotation, "manually_on_variant")
        self.assertTrue(product_2.shop_only_quotation, "Other variant shouldn't change")
        # Set false on template should set all variants to false
        template.shop_only_quotation = "never"
        self.assertFalse(product_1.shop_only_quotation)
        self.assertFalse(product_2.shop_only_quotation)
