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

# TODO MIGRATE
#    def test_categories(self):
#        self.assertEqual(
#            len(self.shopinvader_variant.shopinvader_categ_ids), 0)
#        self.backend.bind_all_category()
#        self.shopinvader_variant.invalidate_cache()
#        self.assertEqual(
#            len(self.shopinvader_variant.shopinvader_categ_ids), 2)
#        self.assertEqual(
#            self.shopinvader_variant.shopinvader_categ_ids.mapped('record_id'),
#            self.template.categ_id + self.template.categ_id.parent_id)
#
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

    def test_price_by_qty(self):
        expected_result = {
            'public_tax_exc': {
                'tax_included': False,
                'value': 652.17},
            'public_tax_inc': {
                'tax_included': True,
                'value': 750.0},
            'pro_tax_exc': {
                'tax_included': False,
                'value': 521.74,
            }}
        product = self.shopinvader_variant
        for role in self.backend.role_ids:
            fposition = role.fiscal_position_ids
            if len(fposition) > 0:
                fposition = fposition[0]

            result = product._get_price(
                role.pricelist_id, fposition, self.backend.company_id)
            self.assertDictEqual(expected_result[role.code], result)
