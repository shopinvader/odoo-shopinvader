# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.addons.shopinvader_v1_product.tests.common import ProductCommonCase


class TestCustomerSpecialProduct(ProductCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.ir_export = cls.env.ref("shopinvader_v1_product.ir_exp_shopinvader_variant")
        cls.parser = cls.ir_export.get_json_parser()
        cls.customer = cls.env.ref("base.res_partner_2")
        cls.shopinvader_variant.manufactured_for_partner_ids = [
            (6, 0, cls.customer.ids)
        ]
        cls.category = cls.shopinvader_variant.tmpl_record_id.categ_id
        cls.categ_bind_wizard_model = cls.env["shopinvader.category.binding.wizard"]
        bind_wizard = cls.categ_bind_wizard_model.create(
            {
                "backend_id": cls.backend.id,
                "product_category_ids": [(6, 0, cls.category.ids)],
            }
        )
        bind_wizard.action_bind_categories()

    def test_parser_update(self):
        self.assertIn({"name": "manufactured_for_partners"}, self.parser["fields"])

    def test_extra_fields(self):
        data = self.shopinvader_variant.jsonify(
            {"fields": [{"name": "manufactured_for_partners"}]}, one=True
        )
        self.assertEqual(data["manufactured_for_partners"], self.customer.ids)

    def test_extra_fields_no_value(self):
        # Wipe it and get default empty value
        self.shopinvader_variant.manufactured_for_partner_ids = False
        data = self.shopinvader_variant.jsonify(
            {"fields": [{"name": "manufactured_for_partners"}]}, one=True
        )
        self.assertEqual(data["manufactured_for_partners"], ["_NOVALUE_"])

    def test_redirect_default(self):
        """Ensure product not manufactured for specific partner get redirected."""
        self.assertEqual(
            len(self.category.shopinvader_bind_ids.redirect_url_url_ids), 0
        )
        self.shopinvader_variant.manufactured_for_partner_ids = False
        self.shopinvader_variant.shopinvader_product_id.write({"active": False})
        self.category.shopinvader_bind_ids.invalidate_cache()
        redirect_urls = self.category.shopinvader_bind_ids.redirect_url_url_ids
        self.assertEqual(len(redirect_urls), 1)
        url_key = self.shopinvader_variant.automatic_url_key
        self.assertEqual(redirect_urls.url_key, url_key)

    def test_no_redirect(self):
        """Ensure product manufactured for specific partner does not get redirected."""
        self.assertEqual(
            len(self.category.shopinvader_bind_ids.redirect_url_url_ids), 0
        )
        self.shopinvader_variant.record_id.write({"active": False})
        self.category.shopinvader_bind_ids.invalidate_cache()
        self.assertEqual(
            len(self.category.shopinvader_bind_ids.redirect_url_url_ids), 0
        )
