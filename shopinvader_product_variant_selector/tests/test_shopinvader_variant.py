# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase


class ShopinvaderVariantCase(TransactionCase):
    def setUp(self):
        super(ShopinvaderVariantCase, self).setUp()
        self.backend = self.env.ref("shopinvader.backend_1")
        self.lang = self.env.ref("base.lang_en")
        self.template = self.env.ref(
            "product.product_product_4_product_template"
        )
        self.env.ref("product.product_attribute_2").sequence = 1
        self.env.ref("product.product_attribute_1").sequence = 2
        self.env.ref("product.product_attribute_3").sequence = 3

    def _configure_and_get_variant(self, code):
        self.template.create_variant_ids()
        self.env["shopinvader.product"].with_context(map_children=True).create(
            {
                "backend_id": self.backend.id,
                "lang_id": self.lang.id,
                "record_id": self.template.id,
            }
        )
        for variant in self.template.product_variant_ids:
            values = variant.mapped("attribute_value_ids").sorted(
                lambda s: s.attribute_id.sequence
            )
            variant.default_code = "-".join(values.mapped("name"))
        for variant in self.template.mapped(
            "product_variant_ids.shopinvader_bind_ids"
        ):
            if variant.default_code == code:
                return variant

    def _inactive_variant(self, codes):
        for variant in self.template.mapped(
            "product_variant_ids.shopinvader_bind_ids"
        ):
            if variant.default_code in codes:
                variant.active = False

    def test_selector_with_one_dimension(self):
        self.env.ref("product.product_attribute_line_3").unlink()
        self.env.ref("product.product_attribute_line_2").unlink()
        variant = self._configure_and_get_variant("16 GB")
        self.assertEqual(
            variant.variant_selector,
            [
                {
                    "name": "Memory",
                    "values": [
                        {
                            "name": "16 GB",
                            "sku": "16 GB",
                            "selected": True,
                            "available": True,
                        },
                        {
                            "name": "32 GB",
                            "sku": "32 GB",
                            "selected": False,
                            "available": True,
                        },
                    ],
                }
            ],
        )

    def test_selector_with_two_dimension(self):
        self.env.ref("product.product_attribute_line_3").unlink()
        variant = self._configure_and_get_variant("White-16 GB")
        self.assertEqual(
            variant.variant_selector,
            [
                {
                    "name": "Color",
                    "values": [
                        {
                            "name": "White",
                            "sku": "White-16 GB",
                            "selected": True,
                            "available": True,
                        },
                        {
                            "name": "Black",
                            "sku": "Black-16 GB",
                            "selected": False,
                            "available": True,
                        },
                    ],
                },
                {
                    "name": "Memory",
                    "values": [
                        {
                            "name": "16 GB",
                            "sku": "White-16 GB",
                            "selected": True,
                            "available": True,
                        },
                        {
                            "name": "32 GB",
                            "sku": "White-32 GB",
                            "selected": False,
                            "available": True,
                        },
                    ],
                },
            ],
        )

    def test_selector_with_two_dimension_and_inactive(self):
        self.env.ref("product.product_attribute_line_3").unlink()
        variant = self._configure_and_get_variant("White-16 GB")
        self._inactive_variant(["White-32 GB"])
        self.assertEqual(
            variant.variant_selector,
            [
                {
                    "name": "Color",
                    "values": [
                        {
                            "name": "White",
                            "sku": "White-16 GB",
                            "selected": True,
                            "available": True,
                        },
                        {
                            "name": "Black",
                            "sku": "Black-16 GB",
                            "selected": False,
                            "available": True,
                        },
                    ],
                },
                {
                    "name": "Memory",
                    "values": [
                        {
                            "name": "16 GB",
                            "sku": "White-16 GB",
                            "selected": True,
                            "available": True,
                        },
                        {
                            "name": "32 GB",
                            "sku": "",
                            "selected": False,
                            "available": False,
                        },
                    ],
                },
            ],
        )

    def test_selector_with_three_dimension_and_inactive(self):
        value = self.env["product.attribute.value"].create(
            {
                "attribute_id": self.ref("product.product_attribute_3"),
                "name": "42 GHz",
            }
        )
        self.env.ref("product.product_attribute_line_3").write(
            {"value_ids": [(4, value.id)]}
        )
        variant = self._configure_and_get_variant("White-16 GB-2.4 GHz")
        self._inactive_variant(["White-32 GB-2.4 GHz", "White-16 GB-42 GHz"])
        self.assertEqual(
            variant.variant_selector,
            [
                {
                    "name": "Color",
                    "values": [
                        {
                            "name": "White",
                            "sku": "White-16 GB-2.4 GHz",
                            "selected": True,
                            "available": True,
                        },
                        {
                            "name": "Black",
                            "sku": "Black-16 GB-2.4 GHz",
                            "selected": False,
                            "available": True,
                        },
                    ],
                },
                {
                    "name": "Memory",
                    "values": [
                        {
                            "name": "16 GB",
                            "sku": "White-16 GB-2.4 GHz",
                            "selected": True,
                            "available": True,
                        },
                        {
                            "name": "32 GB",
                            "sku": "White-32 GB-42 GHz",
                            "selected": False,
                            "available": True,
                        },
                    ],
                },
                {
                    "name": "Wi-Fi",
                    "values": [
                        {
                            "name": "2.4 GHz",
                            "sku": "White-16 GB-2.4 GHz",
                            "selected": True,
                            "available": True,
                        },
                        {
                            "name": "42 GHz",
                            "sku": "",
                            "selected": False,
                            "available": False,
                        },
                    ],
                },
            ],
        )
