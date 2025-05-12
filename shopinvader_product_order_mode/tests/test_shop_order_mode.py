# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestShopOrderMode(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Define different attributes to allow to have mulitple products for the same template
        cls.test_attribute = cls.env["product.attribute"].create(
            {"name": "Test attribute"}
        )
        cls.test_attribute_1 = cls.env["product.attribute.value"].create(
            {"name": "Test attribute value 1", "attribute_id": cls.test_attribute.id}
        )
        cls.test_attribute_2 = cls.env["product.attribute.value"].create(
            {"name": "Test attribute value 2", "attribute_id": cls.test_attribute.id}
        )

        cls.template = cls.env["product.template"].create(
            {
                "name": "Test Product Template",
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.test_attribute.id,
                            "value_ids": [
                                Command.link(cls.test_attribute_1.id),
                                Command.link(cls.test_attribute_2.id),
                            ],
                        }
                    )
                ],
                "shop_order_mode": "direct_sale_only",
                "is_shop_order_mode_unabled_on_variant": False,
            }
        )

        cls.product = cls.template.product_variant_ids[0]
        cls.product_2 = cls.template.product_variant_ids[1]

    def test_default_order_mode_on_products(self):
        """
        Test that products order mode is initiated to the order mode of the template.
        """
        self.assertEqual(self.product.shop_order_mode, self.template.shop_order_mode)

    def test_product_shop_order_mode_constraint(self):
        """
        Test that the shop_order_mode field on product.product is not editable
        when is_shop_order_mode_unabled_on_variant is False on product.template.
        """

        with self.assertRaises(ValidationError):
            self.product.shop_order_mode = None

        self.template.is_shop_order_mode_unabled_on_variant = True

        self.product.shop_order_mode = None
        self.assertNotEqual(self.product.shop_order_mode, "direct_sale_only")
        self.assertEqual(self.template.shop_order_mode, "direct_sale_only")

    def test_shop_order_mode_reset(self):
        """
        Test that the `shop_order_mode` field on product.product is reset to the
        value of the product.template when `is_shop_order_mode_unabled_on_variant` is True.
        """
        self.template.is_shop_order_mode_unabled_on_variant = True
        self.product.shop_order_mode = None
        self.template.is_shop_order_mode_unabled_on_variant = False
        self.assertEqual(self.product.shop_order_mode, self.template.shop_order_mode)
