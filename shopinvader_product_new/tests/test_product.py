# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProductNew(TransactionCase):
    def setUp(self):
        super().setUp()
        self.backend = self.env.ref("shopinvader.backend_1")
        self.backend.bind_all_product()

    def test_scheduler_new_product(self):
        self.env["product.template"].compute_new_product(10, extra_domain=[])
        new_products = self.env["product.template"].search([("new_product", "=", True)])
        self.assertEqual(len(new_products), 10)
        product = self.env["product.template"].create(
            {"name": "Test new product", "default_code": "REF-NEW-PRODUCT"}
        )
        self.backend.bind_all_product()
        self.assertEqual(product.new_product, False)
        self.env["product.template"].compute_new_product(10, extra_domain=[])
        self.assertEqual(product.new_product, True)
        new_products = self.env["product.template"].search([("new_product", "=", True)])
        self.assertEqual(len(new_products), 10)
