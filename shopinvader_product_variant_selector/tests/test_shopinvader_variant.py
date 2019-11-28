# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import SavepointCase


class ShopinvaderVariantCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        ref = cls.env.ref
        cls.backend = ref("shopinvader.backend_1")
        cls.lang = ref("base.lang_en")
        cls.template = cls.mref("product_template_1")
        cls.maxDiff = None

    @classmethod
    def mref(cls, key):
        return cls.env.ref(
            "shopinvader_product_variant_selector.{}".format(key)
        )

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
                # We volontary return a new browse record to avoid useless
                # recompute linked to the prefetch
                return self.env["shopinvader.variant"].browse(variant.id)

    def _inactive_variant(self, codes):
        for variant in self.template.mapped(
            "product_variant_ids.shopinvader_bind_ids"
        ):
            if variant.default_code in codes:
                variant.active = False

    def test_selector_with_one_dimension(self):
        self.mref("product_attribute_line_2").unlink()
        self.mref("product_attribute_line_3").unlink()
        variant = self._configure_and_get_variant("Poster")
        self.assertEqual(
            variant.variant_selector,
            [
                {
                    "name": "Frame Type",
                    "values": [
                        {
                            "name": "Poster",
                            "sku": "Poster",
                            "selected": True,
                            "available": True,
                        },
                        {
                            "name": "Wooden",
                            "sku": "Wooden",
                            "selected": False,
                            "available": True,
                        },
                    ],
                }
            ],
        )

    def test_selector_with_two_dimension(self):
        self.mref("product_attribute_line_3").unlink()
        variant = self._configure_and_get_variant("Poster-White")
        self.assertEqual(
            variant.variant_selector,
            [
                {
                    "name": "Frame Type",
                    "values": [
                        {
                            "name": "Poster",
                            "sku": "Poster-White",
                            "selected": True,
                            "available": True,
                        },
                        {
                            "name": "Wooden",
                            "sku": "Wooden-White",
                            "selected": False,
                            "available": True,
                        },
                    ],
                },
                {
                    "name": "Frame Color",
                    "values": [
                        {
                            "name": "White",
                            "sku": "Poster-White",
                            "selected": True,
                            "available": True,
                        },
                        {
                            "name": "Black",
                            "sku": "Poster-Black",
                            "selected": False,
                            "available": True,
                        },
                        {
                            "name": "Grey",
                            "sku": "Poster-Grey",
                            "selected": False,
                            "available": True,
                        },
                    ],
                },
            ],
        )

    def test_selector_with_two_dimension_and_inactive(self):
        self.mref("product_attribute_line_3").unlink()
        variant = self._configure_and_get_variant("Poster-White")
        self._inactive_variant(["Poster-Black"])
        self.assertEqual(
            variant.variant_selector,
            [
                {
                    "name": "Frame Type",
                    "values": [
                        {
                            "name": "Poster",
                            "sku": "Poster-White",
                            "selected": True,
                            "available": True,
                        },
                        {
                            "name": "Wooden",
                            "sku": "Wooden-White",
                            "selected": False,
                            "available": True,
                        },
                    ],
                },
                {
                    "name": "Frame Color",
                    "values": [
                        {
                            "name": "White",
                            "sku": "Poster-White",
                            "selected": True,
                            "available": True,
                        },
                        {
                            "name": "Black",
                            "sku": "",
                            "selected": False,
                            "available": False,
                        },
                        {
                            "name": "Grey",
                            "sku": "Poster-Grey",
                            "selected": False,
                            "available": True,
                        },
                    ],
                },
            ],
        )

    def test_selector_with_three_dimension_and_inactive(self):
        variant = self._configure_and_get_variant("Poster-White-70x50cm")
        self._inactive_variant(["Poster-White-45x30cm"])
        self.assertEqual(
            variant.variant_selector,
            [
                {
                    "name": "Frame Type",
                    "values": [
                        {
                            "name": "Poster",
                            "sku": "Poster-White-70x50cm",
                            "selected": True,
                            "available": True,
                        },
                        {
                            "name": "Wooden",
                            "sku": "Wooden-White-70x50cm",
                            "selected": False,
                            "available": True,
                        },
                    ],
                },
                {
                    "name": "Frame Color",
                    "values": [
                        {
                            "name": "White",
                            "sku": "Poster-White-70x50cm",
                            "selected": True,
                            "available": True,
                        },
                        {
                            "name": "Black",
                            "sku": "Poster-Black-70x50cm",
                            "selected": False,
                            "available": True,
                        },
                        {
                            "name": "Grey",
                            "sku": "Poster-Grey-70x50cm",
                            "selected": False,
                            "available": True,
                        },
                    ],
                },
                {
                    "name": "Poster Size",
                    "values": [
                        {
                            "name": "45x30cm",
                            "sku": "",
                            "selected": False,
                            "available": False,
                        },
                        {
                            "name": "70x50cm",
                            "sku": "Poster-White-70x50cm",
                            "selected": True,
                            "available": True,
                        },
                        {
                            "name": "90x60cm",
                            "sku": "Poster-White-90x60cm",
                            "selected": False,
                            "available": True,
                        },
                    ],
                },
            ],
        )

    def test_selector_with_three_dimension_with_many_inactive(self):
        variant = self._configure_and_get_variant("Poster-White-70x50cm")
        # We make inactive all Wooden product than match the White
        # and 70x50cm value in order to force the system to propose
        # for the selector Frame Type a variant that does not match
        # these 2 values
        self._inactive_variant(
            [
                "Poster-White-45x30cm",
                "Wooden-White-45x30cm",
                "Wooden-White-70x50cm",
                "Wooden-White-90x60cm",
                "Wooden-Black-70x50cm",
                "Poster-Black-70x50cm",
            ]
        )
        self.assertEqual(
            variant.variant_selector,
            [
                {
                    "name": "Frame Type",
                    "values": [
                        {
                            "name": "Poster",
                            "sku": "Poster-White-70x50cm",
                            "selected": True,
                            "available": True,
                        },
                        {
                            "name": "Wooden",
                            "sku": "Wooden-Black-45x30cm",
                            "selected": False,
                            "available": True,
                        },
                    ],
                },
                {
                    "name": "Frame Color",
                    "values": [
                        {
                            "name": "White",
                            "sku": "Poster-White-70x50cm",
                            "selected": True,
                            "available": True,
                        },
                        {
                            "name": "Black",
                            "sku": "Poster-Black-45x30cm",
                            "selected": False,
                            "available": True,
                        },
                        {
                            "name": "Grey",
                            "sku": "Poster-Grey-70x50cm",
                            "selected": False,
                            "available": True,
                        },
                    ],
                },
                {
                    "name": "Poster Size",
                    "values": [
                        {
                            "name": "45x30cm",
                            "sku": "",
                            "selected": False,
                            "available": False,
                        },
                        {
                            "name": "70x50cm",
                            "sku": "Poster-White-70x50cm",
                            "selected": True,
                            "available": True,
                        },
                        {
                            "name": "90x60cm",
                            "sku": "Poster-White-90x60cm",
                            "selected": False,
                            "available": True,
                        },
                    ],
                },
            ],
        )
