# -*- coding: utf-8 -*-
# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.exceptions import UserError

from .common import ProductCommonCase


class TestRedirect(ProductCommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestRedirect, cls).setUpClass()
        cls.backend.bind_all_category()
        cls.backend.bind_all_product()

    def test_redirect_category(self):
        dest_categ = self.env.ref("product.product_category_1")
        categ_2 = self.env.ref("product.product_category_2")
        categ_3 = self.env.ref("product.product_category_3")

        wizard = (
            self.env["shopinvader.redirection.wizard"]
            .with_context(
                {
                    "active_model": "product.category",
                    "active_ids": [categ_2.id, categ_3.id],
                }
            )
            .create({})
        )
        wizard.dest_categ_id = dest_categ.id
        wizard.apply_redirection()

        urls = dest_categ.shopinvader_bind_ids.redirect_url_url_ids.mapped(
            "url_key"
        )

        self.assertEqual(set(urls), {"all/internal", "all/saleable/services"})
        self.assertEqual(
            dest_categ.shopinvader_bind_ids.url_key, "all/saleable"
        )

        self.assertEqual(len(categ_2.shopinvader_bind_ids.url_url_ids), 0)
        self.assertEqual(len(categ_3.shopinvader_bind_ids.url_url_ids), 0)
        self.assertFalse(categ_2.shopinvader_bind_ids.active)
        self.assertFalse(categ_3.shopinvader_bind_ids.active)

    def test_redirect_product(self):
        dest_product = self.env.ref(
            "product.product_product_1_product_template"
        )
        product_2 = self.env.ref("product.product_product_2_product_template")
        product_3 = self.env.ref("product.product_product_3_product_template")

        wizard = (
            self.env["shopinvader.redirection.wizard"]
            .with_context(
                {
                    "active_model": "product.template",
                    "active_ids": [product_2.id, product_3.id],
                }
            )
            .create({})
        )
        wizard.dest_product_id = dest_product.id
        wizard.apply_redirection()

        urls = dest_product.shopinvader_bind_ids.redirect_url_url_ids.mapped(
            "url_key"
        )

        self.assertEqual(
            set(urls), {"computer-sc234-pcsc234", "support-services"}
        )
        self.assertEqual(
            dest_product.shopinvader_bind_ids.url_key, "gap-analysis-service"
        )

        self.assertEqual(len(product_2.shopinvader_bind_ids.url_url_ids), 0)
        self.assertEqual(len(product_3.shopinvader_bind_ids.url_url_ids), 0)
        self.assertFalse(product_2.shopinvader_bind_ids.active)
        self.assertFalse(product_3.shopinvader_bind_ids.active)

    def test_redirect_on_itself(self):
        dest_product = self.env.ref(
            "product.product_product_1_product_template"
        )
        wizard = (
            self.env["shopinvader.redirection.wizard"]
            .with_context(
                {
                    "active_model": "product.template",
                    "active_ids": [dest_product.id],
                }
            )
            .create({})
        )
        wizard.dest_product_id = dest_product.id
        with self.assertRaises(UserError):
            wizard.apply_redirection()
