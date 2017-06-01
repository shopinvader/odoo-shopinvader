# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp.addons.shopinvader.tests.common import ProductCommonCase


class ProductCase(ProductCommonCase):

    def test_one_categories(self):
        self.backend.bind_all_category()
        self.assertEqual(
            self.template.categ_id + self.template.categ_id.parent_id,
            self.shopinvader_variant.categories.mapped('record_id'))

    def test_multi_categories(self):
        self.backend.bind_all_category()
        categs = self.env['product.category'].search(
            [('id', '!=', self.template.categ_id.id)])
        self.template.categ_ids = categs
        self.assertEqual(
            self.template.categ_id + categs,
            self.shopinvader_variant.categories.mapped('record_id'))
