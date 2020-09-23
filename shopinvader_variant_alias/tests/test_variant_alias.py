# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_backend import BackendCase


class TestVariantAlias(BackendCase):
    @classmethod
    def setUpClass(cls):
        super(TestVariantAlias, cls).setUpClass()
        cls.product = cls.env.ref("shopinvader.product_product_44")

    def test_variant_attributes(self):
        attribute = self.env.ref("product.product_attribute_1")
        value_1 = self.env.ref("product.product_attribute_value_1")
        alias_1 = "alias 1"
        value_1.shopinvader_alias = alias_1
        value_2 = self.env.ref("product.product_attribute_value_2")
        alias_2 = "alias 2"
        value_2.shopinvader_alias = alias_2
        values = value_1 + value_2

        product_template = self.env["product.template"].create(
            {
                "name": "consume",
                "attribute_line_ids": [
                    (
                        0,
                        False,
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [(6, False, values.ids)],
                        },
                    )
                ],
            }
        )
        self._bind_all_product()
        shopinvader_variants = product_template.mapped(
            "shopinvader_bind_ids.shopinvader_variant_ids"
        )

        v1 = shopinvader_variants[0]
        variant_value_1 = v1.variant_attributes[attribute.name.lower()]
        self.assertEquals(variant_value_1, alias_1)

        v2 = shopinvader_variants[1]
        variant_value_2 = v2.variant_attributes[attribute.name.lower()]
        self.assertEquals(variant_value_2, alias_2)
