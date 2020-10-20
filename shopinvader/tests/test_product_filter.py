# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from .common import CommonCase


class TestProductFilter(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.shopinvader_product_field = cls.env["ir.model.fields"].search(
            [("model", "=", "shopinvader.product"), ("name", "=", "name")],
            limit=1,
        )
        cls.variant_attribute = cls.env["product.attribute"].search(
            [("name", "=", "Legs")], limit=1
        )
        cls._install_lang(cls, "base.lang_fr")

        cls.variant_attribute.with_context(lang="fr_FR").name = "Jambes"

        cls.filter_on_field = cls.env["product.filter"].create(
            {
                "name": "Product Name",
                "based_on": "field",
                "field_id": cls.shopinvader_product_field.id,
            }
        )
        cls.filter_on_attr = cls.env["product.filter"].create(
            {
                "name": "Test Filter on field name",
                "based_on": "variant_attribute",
                "variant_attribute_id": cls.variant_attribute.id,
            }
        )

    def test_product_filter_field_name(self):
        self.assertEqual(self.filter_on_field.display_name, "name")

    def test_product_filter_attribute_name(self):
        self.assertEqual(
            self.filter_on_attr.display_name, "variant_attributes.legs"
        )
        self.assertEqual(
            self.filter_on_attr.with_context(lang="fr_FR").display_name,
            "variant_attributes.jambes",
        )

    def test_delete_attribute_delete_filter_cascade(self):
        product_attribute = self.env["product.attribute"].create(
            {"name": "Test delete", "create_variant": "no_variant"}
        )
        filter1 = self.env["product.filter"].create(
            {
                "name": "Test Filter delete",
                "based_on": "variant_attribute",
                "variant_attribute_id": product_attribute.id,
            }
        )
        product_attribute.unlink()
        self.assertFalse(filter1.exists())
