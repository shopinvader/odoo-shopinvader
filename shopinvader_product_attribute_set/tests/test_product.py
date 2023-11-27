# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from odoo.addons.extendable.tests.common import ExtendableMixin
from odoo.addons.shopinvader_product.schemas import ProductProduct

from ..schemas import ProductAttributeType


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
        cls.group = cls.env["attribute.group"].create(
            {
                "name": "My Group",
                "model_id": cls.env.ref("product.model_product_product").id,
            }
        )

    def _create_attribute(self, vals):
        vals.update(
            {
                "nature": "custom",
                "model_id": self.env.ref("product.model_product_product").id,
                "field_description": "Attribute %s" % vals["attribute_type"],
                "name": "x_%s" % vals["attribute_type"],
                "attribute_group_id": self.group.id,
            }
        )
        return self.env["attribute.attribute"].create(vals)

    def test_product_attributes(self):
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
        self.maxDiff = None
        self.assertListEqual(
            res.get("structured_attributes"),
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
                            "type": ProductAttributeType.boolean,
                        },
                        {
                            "value": "Intel i5",
                            "name": "Processor",
                            "key": "processor",
                            "type": ProductAttributeType.select,
                        },
                        {
                            "value": "foo",
                            "name": "Technical Description",
                            "key": "technical_description",
                            "type": ProductAttributeType.text,
                        },
                    ],
                }
            ],
        )

    def test_product_attributes_empty_select(self):
        self.product.write({"attribute_set_id": self.attr_set.id, "x_processor": False})
        res = ProductProduct.from_product_product(self.product).model_dump()
        self.assertEqual(res["attributes"]["processor"], "")

        processor_field = {}
        for field in res["structured_attributes"][0]["fields"]:
            if field["key"] == "processor":
                processor_field = field
        self.assertEqual(
            processor_field,
            {
                "value": "",
                "name": "Processor",
                "key": "processor",
                "type": ProductAttributeType.select,
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
        self.maxDiff = None
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
                            "type": ProductAttributeType.boolean,
                        },
                        {
                            "value": "Intel i5",
                            "name": "Processor",
                            "key": "processor",
                            "type": ProductAttributeType.select,
                        },
                        {
                            "value": "foo",
                            "name": "Technical Description",
                            "key": "technical_description",
                            "type": ProductAttributeType.text,
                        },
                    ],
                }
            ],
        )

    def test_product_data_no_attribute_set(self):
        res = ProductProduct.from_product_product(self.product).model_dump()
        self.assertEqual(res.get("attributes"), {})
        self.assertEqual(res.get("structured_attributes"), [])

    def test_product_data_select_multi_select_attributes(self):
        attribute_select = self._create_attribute(
            {
                "attribute_type": "select",
                "option_ids": [
                    (0, 0, {"name": "Value 1"}),
                    (0, 0, {"name": "Value 2"}),
                ],
            }
        )
        attribute_multi_select = self._create_attribute(
            {
                "attribute_type": "multiselect",
                "option_ids": [
                    (0, 0, {"name": "Value 1"}),
                    (0, 0, {"name": "Value 2"}),
                ],
            }
        )
        self.attr_set.attribute_ids = attribute_select | attribute_multi_select
        self.product.write(
            {
                "attribute_set_id": self.attr_set.id,
                "x_select": attribute_select.option_ids[0].id,
                "x_multiselect": [(6, 0, attribute_multi_select.option_ids.ids)],
            }
        )
        # TODO need to investigate why we need to reset the registry after the
        # creation of new odoo fields
        self.reset_extendable_registry()
        self.init_extendable_registry()
        res = ProductProduct.from_product_product(self.product).model_dump()
        self.assertEqual(
            res.get("attributes"),
            {"select": "Value 1", "multiselect": ["Value 1", "Value 2"]},
        )
        self.maxDiff = None
        self.assertListEqual(
            res.get("structured_attributes"),
            [
                {
                    "group_name": "My Group",
                    "fields": [
                        {
                            "value": "Value 1",
                            "name": "Attribute select",
                            "key": "select",
                            "type": ProductAttributeType.select,
                        },
                        {
                            "value": ["Value 1", "Value 2"],
                            "name": "Attribute multiselect",
                            "key": "multiselect",
                            "type": ProductAttributeType.multiselect,
                        },
                    ],
                }
            ],
        )
