# -*- coding: utf-8 -*-
# Copyright 2017-2018 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader.tests.common import ProductCommonCase


class ProductCase(ProductCommonCase):
    def setUp(self):
        super(ProductCase, self).setUp()
        self.env["product.category"]._parent_store_compute()

    def test_one_categories(self):
        self.backend.bind_all_category()
        categ = self.template.categ_id
        categs = categ + categ.parent_id + categ.parent_id.parent_id
        self.assertEqual(
            categs,
            self.shopinvader_variant.shopinvader_categ_ids.mapped("record_id"),
        )

    def test_multi_categories(self):
        self.backend.bind_all_category()
        categs = self.env["product.category"].search(
            [("id", "!=", self.template.categ_id.id)]
        )
        self.template.categ_ids = categs
        self.assertEqual(
            self.template.categ_id + categs,
            self.shopinvader_variant.shopinvader_categ_ids.mapped("record_id"),
        )
