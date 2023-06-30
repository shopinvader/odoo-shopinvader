# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import exceptions
from odoo.tools import mute_logger

from .common import CommonCase


class TestProductFilter(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._install_lang(cls, "base.lang_fr")
        model = cls.env["ir.model"].search(
            [("model", "=", "shopinvader.product")], limit=1
        )
        # add custom field so that we can delete it (cannot do it w/ modules' fields)
        cls.shopinvader_product_field = cls.env["ir.model.fields"].create(
            {
                "model_id": model.id,
                "name": "x_custom_field",
                "field_description": "Custom field for testing",
                "ttype": "char",
            }
        )
        cls.variant_attribute = cls.env["product.attribute"].create(
            {"name": "Test attribute", "create_variant": "no_variant"}
        )

        cls.variant_attribute.with_context(lang="fr_FR").name = "Test attribute FR"

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
        self.assertEqual(self.filter_on_field.display_name, "x_custom_field")
        self.assertEqual(
            self.filter_on_field.with_context(lang="fr_FR").display_name,
            "x_custom_field",
        )

    def test_product_filter_field_name_with_path(self):
        self.filter_on_field.path = "x_custom_field.inner_value"
        self.assertEqual(
            self.filter_on_field.display_name, "x_custom_field.inner_value"
        )
        self.assertEqual(
            self.filter_on_field.with_context(lang="fr_FR").display_name,
            "x_custom_field.inner_value",
        )

    def test_product_filter_attribute_name(self):
        self.assertEqual(
            self.filter_on_attr.display_name,
            "variant_attributes.test_attribute",
        )
        self.assertEqual(
            self.filter_on_attr.with_context(lang="fr_FR").display_name,
            "variant_attributes.test_attribute_fr",
        )

    @mute_logger("odoo.models.unlink")
    def test_delete_field_delete_filter_cascade(self):
        self.shopinvader_product_field.unlink()
        self.assertFalse(self.filter_on_field.exists())

    @mute_logger("odoo.models.unlink")
    def test_delete_attribute_delete_filter_cascade(self):
        self.variant_attribute.unlink()
        self.assertFalse(self.filter_on_attr.exists())

    def test_product_filter_field_constrains(self):
        with self.assertRaises(exceptions.UserError) as err:
            self.filter_on_field.write({"field_id": False})
        self.assertEqual(
            err.exception.name,
            "Product filter ID=%d is based on field: "
            "requires a field!" % self.filter_on_field.id,
        )

    def test_product_filter_attr_constrains(self):
        with self.assertRaises(exceptions.UserError) as err:
            self.filter_on_attr.write({"variant_attribute_id": False})
        self.assertEqual(
            err.exception.name,
            "Product filter ID=%d is based on variant attribute: "
            "requires an attribute!" % self.filter_on_attr.id,
        )
