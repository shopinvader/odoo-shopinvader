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
        self.template_group = self.env["attribute.group"].create(
            {
                "name": "Test Group",
                "model_id": self.env.ref("product.model_product_template").id,
            }
        )

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
        self.product.write({"attribute_set_id": self.attr_set.id, "x_processor": False})

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

    def test_native_attribute_char(self):
        self.env["attribute.attribute"].create(
            {
                "nature": "native",
                "field_id": self.env.ref(
                    "product.field_product_template__default_code"
                ).id,
                "attribute_set_ids": [(6, 0, [self.attr_set.id])],
                "attribute_group_id": self.template_group.id,
            }
        )
        self.product.write({"attribute_set_id": self.attr_set.id})
        self.assertEqual(
            self.shopinvader_variant.attributes["default_code"],
            self.product.default_code,
        )

    def test_native_attribute_many2one(self):
        self.env["attribute.attribute"].create(
            {
                "nature": "native",
                "field_id": self.env.ref("product.field_product_template__categ_id").id,
                "attribute_set_ids": [(6, 0, [self.attr_set.id])],
                "attribute_group_id": self.template_group.id,
            }
        )
        self.product.write({"attribute_set_id": self.attr_set.id})
        self.assertEqual(
            self.shopinvader_variant.attributes["categ_id"],
            self.product.categ_id.name,
        )

    def test_native_attribute_boolean(self):
        self.env["attribute.attribute"].create(
            {
                "nature": "native",
                "field_id": self.env.ref("product.field_product_template__rental").id,
                "attribute_set_ids": [(6, 0, [self.attr_set.id])],
                "attribute_group_id": self.template_group.id,
            }
        )
        self.product.write({"attribute_set_id": self.attr_set.id})
        self.assertEqual(
            self.shopinvader_variant.attributes["rental"], self.product.rental
        )
        rental_field = {}
        for field in self.shopinvader_variant.structured_attributes[1]["fields"]:
            if field["key"] == "rental":
                rental_field = field
        self.assertEqual(
            rental_field,
            {
                "value": "false",
                "name": "Can be Rent",
                "key": "rental",
                "type": "boolean",
            },
        )

    def test_native_attribute_selection(self):
        self.env["attribute.attribute"].create(
            {
                "nature": "native",
                "field_id": self.env.ref("product.field_product_template__type").id,
                "attribute_set_ids": [(6, 0, [self.attr_set.id])],
                "attribute_group_id": self.template_group.id,
            }
        )
        self.product.write({"attribute_set_id": self.attr_set.id})
        self.assertEqual(
            self.shopinvader_variant.attributes["type"],
            self.product.type,
        )

    def test_native_attribute_float(self):
        self.env["attribute.attribute"].create(
            {
                "nature": "native",
                "field_id": self.env.ref("product.field_product_template__weight").id,
                "attribute_set_ids": [(6, 0, [self.attr_set.id])],
                "attribute_group_id": self.template_group.id,
            }
        )
        self.product.write({"attribute_set_id": self.attr_set.id})
        weight_field = {}
        for field in self.shopinvader_variant.structured_attributes[1]["fields"]:
            if field["key"] == "weight":
                weight_field = field
        self.assertEqual(
            weight_field,
            {
                "value": "9.54",
                "name": "Weight",
                "key": "weight",
                "type": "float",
            },
        )
        self.assertEqual(
            self.shopinvader_variant.attributes["weight"],
            self.product.weight,
        )
