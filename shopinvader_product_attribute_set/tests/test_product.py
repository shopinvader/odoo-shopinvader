# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from odoo.addons.extendable.tests.common import ExtendableMixin
from odoo.addons.shopinvader_product.schemas import ProductProduct


class ProductCase(TransactionCase, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.init_extendable_registry()
        cls.addClassCleanup(cls.reset_extendable_registry)

        cls.attr_set = cls.env.ref("product_attribute_set.computer_attribute_set")
        cls.processor = cls.env.ref(
            "product_attribute_set.computer_processor_attribute_option_1"
        )
        cls.product = cls.env.ref("product.product_product_8")
        attributes = cls.attr_set.attribute_ids.filtered(
            lambda s: s.name
            in ["x_linux_compatible", "x_processor", "x_technical_description"]
        )
        cls.attr_set.attribute_ids = attributes

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
            self.product.attributes,
            {
                "linux_compatible": True,
                "processor": "Intel i5",
                "technical_description": "foo",
            },
        )
        self.assertListEqual(
            self.product.structured_attributes,
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

    def test_product_attributes_empty_select(self):
        self.product.write({"attribute_set_id": self.attr_set.id, "x_processor": False})

        self.assertEqual(self.product.attributes["processor"], "")

        processor_field = {}
        for field in self.product.structured_attributes[0]["fields"]:
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

    def test_product_data(self):
        self.product.write(
            {
                "attribute_set_id": self.attr_set.id,
                "x_linux_compatible": True,
                "x_processor": self.processor.id,
                "x_technical_description": "foo",
            }
        )
        res = ProductProduct.from_product_product(self.product).model_dump()
        self.assertEqual(
            res.get("attributes"),
            {
                "linux_compatible": True,
                "processor": "Intel i5",
                "technical_description": "foo",
            },
        )
        self.assertListEqual(
            res.get("structured_attributes"),
            [
                {
                    "group_name": "Technical",
                    "fields": [
                        {
                            "value": "true",
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

    def test_product_data_no_attribute_set(self):
        res = ProductProduct.from_product_product(self.product).model_dump()
        self.assertEqual(res.get("attributes"), {})
        self.assertEqual(res.get("structured_attributes"), [{}])
