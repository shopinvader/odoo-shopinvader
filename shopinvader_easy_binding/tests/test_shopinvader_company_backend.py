# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestCompanyNewsletter(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.shop_backend_1 = cls.env.ref("shopinvader.backend_1")
        cls.shop_backend_2 = cls.env.ref("shopinvader.backend_2")
        cls.company = cls.env.ref("base.main_company")
        cls.company.shopinvader_company_backend_id = cls.shop_backend_1
        cls.product = cls.env["product.product"].create({"name": "Test Product"})
        cls.product_tmpl = cls.product.product_tmpl_id

    def test_company_backend_mixin(self):
        self.assertEqual(
            self.product.shopinvader_company_backend_id,
            self.shop_backend_1,
        )
        self.assertEqual(
            self.product._ensure_shopinvader_company_backend(),
            self.shop_backend_1,
        )

    def test_company_backend_mixin_no_backend(self):
        self.company.shopinvader_company_backend_id = False
        self.assertFalse(self.product.shopinvader_company_backend_id)
        with self.assertRaises(UserError):
            self.product._ensure_shopinvader_company_backend()

    def test_product_publish(self):
        self.assertFalse(self.product.company_shopinvader_published)
        self.assertFalse(self.product.company_shopinvader_bind_ids)
        # Publish
        self.product.company_shopinvader_published = True
        self.assertTrue(self.product.company_shopinvader_published)
        self.assertTrue(self.product.company_shopinvader_bind_ids.filtered("active"))
        self.assertTrue(self.product.shopinvader_bind_ids.filtered("active"))
        # Unpublish
        self.product.company_shopinvader_published = False
        self.assertFalse(self.product.company_shopinvader_published)
        self.assertFalse(self.product.company_shopinvader_bind_ids.filtered("active"))
        self.assertFalse(self.product.shopinvader_bind_ids.filtered("active"))

    def test_product_template_publish(self):
        self.assertFalse(self.product_tmpl.company_shopinvader_published)
        self.assertFalse(self.product_tmpl.company_shopinvader_bind_ids)
        # Publish
        self.product_tmpl.company_shopinvader_published = True
        self.assertTrue(self.product_tmpl.company_shopinvader_published)
        self.assertTrue(
            self.product_tmpl.company_shopinvader_bind_ids.filtered("active")
        )
        self.assertTrue(self.product_tmpl.shopinvader_bind_ids.filtered("active"))
        # Unpublish
        self.product_tmpl.company_shopinvader_published = False
        self.assertFalse(self.product_tmpl.company_shopinvader_published)
        self.assertFalse(
            self.product_tmpl.company_shopinvader_bind_ids.filtered("active")
        )
        self.assertFalse(self.product_tmpl.shopinvader_bind_ids.filtered("active"))

    def test_product_product_published_search(self):
        self.assertNotIn(
            self.product,
            self.env["product.product"].search(
                [("company_shopinvader_published", "=", True)]
            ),
        )
        self.assertIn(
            self.product,
            self.env["product.product"].search(
                [("company_shopinvader_published", "=", False)]
            ),
        )
        self.product.company_shopinvader_published = True
        self.assertIn(
            self.product,
            self.env["product.product"].search(
                [("company_shopinvader_published", "!=", False)]
            ),
        )
        self.assertNotIn(
            self.product,
            self.env["product.product"].search(
                [("company_shopinvader_published", "!=", True)]
            ),
        )

    def test_product_template_published_search(self):
        self.assertNotIn(
            self.product_tmpl,
            self.env["product.template"].search(
                [("company_shopinvader_published", "=", True)]
            ),
        )
        self.assertIn(
            self.product_tmpl,
            self.env["product.template"].search(
                [("company_shopinvader_published", "=", False)]
            ),
        )
        self.product_tmpl.company_shopinvader_published = True
        self.assertIn(
            self.product_tmpl,
            self.env["product.template"].search(
                [("company_shopinvader_published", "!=", False)]
            ),
        )
        self.assertNotIn(
            self.product_tmpl,
            self.env["product.template"].search(
                [("company_shopinvader_published", "!=", True)]
            ),
        )
