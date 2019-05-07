# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import ProductCommonCase


class ProductCase(ProductCommonCase):
    def setUp(self):
        super(ProductCase, self).setUp()
        self.attr_set = self.env.ref(
            "product_custom_attribute.computer_attribute_set"
        )
        self.processor = self.env.ref(
            "product_custom_attribute.computer_processor_attribute_option_1"
        )
        self.product = self.env.ref("product.product_product_8")
        self.shopinvader_variant = self.product.shopinvader_bind_ids
        self.product_filter = self.env.ref(
            "shopinvader_custom_attribute.filter_compatible_linux"
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
                u"linux_compatible": True,
                u"processor": u"Intel i5",
                u"technical_description": u"foo",
            },
        )

        self.assertEqual(
            self.shopinvader_variant.structured_attributes,
            [
                {
                    "fields": [
                        {
                            "value": u"Intel i5",
                            "name": u"X processor",
                            "key": u"processor",
                        },
                        {
                            "value": u"foo",
                            "name": u"X technical description",
                            "key": u"technical_description",
                        },
                        {
                            "value": True,
                            "name": u"X linux compatible",
                            "key": u"linux_compatible",
                        },
                    ],
                    "group_name": u"Technical",
                }
            ],
        )

    def test_filter(self):
        self.assertEqual(
            self.product_filter.display_name, "attributes.linux_compatible"
        )
