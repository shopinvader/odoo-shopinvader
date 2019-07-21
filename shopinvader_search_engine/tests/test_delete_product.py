# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class BindingCase(TransactionCase):
    def setUp(self):
        super(BindingCase, self).setUp()
        self.template = self.env["product.template"].create({"name": "Test"})
        self.product = self.template.product_variant_ids
        self.shopinvader_product = (
            self.env["shopinvader.product"]
            .with_context(map_children=True)
            .create(
                {
                    "record_id": self.template.id,
                    "backend_id": self.ref("shopinvader.backend_1"),
                    "lang_id": self.ref("base.lang_en"),
                }
            )
        )
        self.shopinvader_variant = (
            self.shopinvader_product.shopinvader_variant_ids
        )


class BindingDoneCase(BindingCase):
    def setUp(self):
        super(BindingDoneCase, self).setUp()
        self.shopinvader_variant.write({"sync_state": "done"})

    def test_unlink_shopinvader_product(self):
        with self.assertRaises(UserError):
            self.shopinvader_product.unlink()

    def test_unlink_product_product(self):
        with self.assertRaises(UserError):
            self.product.unlink()

    def test_unlink_product_template(self):
        with self.assertRaises(UserError):
            self.template.unlink()


class BindingInactiveDoneCase(BindingCase):
    def setUp(self):
        super(BindingInactiveDoneCase, self).setUp()
        self.shopinvader_variant.write({"sync_state": "done", "active": False})

    def test_unlink_shopinvader_product(self):
        self.shopinvader_product.unlink()

    def test_unlink_product_product(self):
        self.product.unlink()

    def test_unlink_product_template(self):
        self.template.unlink()
