# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import ProductCommonCase


class ProductCase(ProductCommonCase):
    def setUp(self):
        super(ProductCase, self).setUp()
        self.attr_set = self.env.ref("product_attribute_set.computer_attribute_set")
        self.processor = self.env.ref(
            "product_attribute_set.computer_processor_attribute_option_1"
        )
        self.product = self.env.ref("product.product_product_8")
        self.shopinvader_variant = self.product.shopinvader_bind_ids
        self.product_filter = self.env.ref(
            "shopinvader_product_attribute_set.filter_compatible_linux"
        )
        attributes = self.attr_set.attribute_ids.filtered(
            lambda s: s.name
            in ["x_linux_compatible", "x_processor", "x_technical_description"]
        )
        self.attr_set.attribute_ids = attributes

    def test_product_attributes(self):
        self.product.write(
            {
                "attribute_set_id": self.attr_set.id,
                "x_linux_compatible": True,
                "x_processor": self.processor.id,
                "x_technical_description": "foo",
            }
        )

        self.assertEqual(
            self.shopinvader_variant.attributes,
            {
                "linux_compatible": True,
                "processor": "Intel i5",
                "technical_description": "foo",
            },
        )
        self.assertListEqual(
            self.shopinvader_variant.structured_attributes,
            [
                {
                    "group_name": "Technical",
                    "fields": [
                        {
                            "value": "true",
                            # TODO cleanup demo in product_attribute_set
                            # name should be "Linux Compatible"
                            "name": "X Linux Compatible",
                            "key": "linux_compatible",
                            "type": "boolean",
                        },
                        {
                            "value": "Intel i5",
                            "name": "Processor",
                            "key": "processor",
                            "type": "select",
                        },
                        {
                            "value": "foo",
                            "name": "Technical Description",
                            "key": "technical_description",
                            "type": "text",
                        },
                    ],
                }
            ],
        )

    def test_filter(self):
        self.assertEqual(
            self.product_filter.display_name, "attributes.linux_compatible"
        )

    def test_product_attributes_empty_select(self):
        self.product.write(
            {
                "attribute_set_id": self.attr_set.id,
                "x_processor": False,
            }
        )

        self.assertEqual(self.shopinvader_variant.attributes["processor"], "")

        processor_field = {}
        for field in self.shopinvader_variant.structured_attributes[0]["fields"]:
            if field["key"] == "processor":
                processor_field = field
        self.assertEqual(
            processor_field,
            {
                "value": "",
                "name": "Processor",
                "key": "processor",
                "type": "select",
            },
        )
