# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import ProductCommonCase


class ProductCase(ProductCommonCase):

    def test_create_shopinvader_variant(self):
        self.assertEqual(
            len(self.template.product_variant_ids),
            len(self.shopinvader_variants))

    def test_categories(self):
        self.assertEqual(
            len(self.shopinvader_variant.shopinvader_categ_ids), 0)
        self.backend.bind_all_category()
        self.shopinvader_variant.invalidate_cache()
        self.assertEqual(
            len(self.shopinvader_variant.shopinvader_categ_ids), 2)
        self.assertEqual(
            self.shopinvader_variant.shopinvader_categ_ids.mapped('record_id'),
            self.template.categ_id + self.template.categ_id.parent_id)

    def test_attributes(self):
        attr_dict = {'color': u'Black',
                     'wi-fi': u'2.4 GHz',
                     'memory': u'16 GB'}
        self.assertDictEqual(self.shopinvader_variant.attributes, attr_dict)

    def test_product_filter(self):
        field_id = self.env['ir.model.fields'].search([
            ('model', '=', 'shopinvader.product'),
            ('name', '=', 'name')])
        filter_on_field = self.env['product.filter'].create(
            {'name': 'Test Filter on field name',
             'based_on': 'field',
             'field_id': field_id.id})
        self.assertEqual(filter_on_field.display_name, 'name')

        attribute_id = self.env['product.attribute'].search([
            ('name', '=', 'Wi-Fi')])
        filter_on_attr = self.env['product.filter'].create(
            {'name': 'Test Filter on field name',
             'based_on': 'attribute',
             'attribute_id': attribute_id.id})
        self.assertEqual(filter_on_attr.display_name, 'attributes.wi-fi')
