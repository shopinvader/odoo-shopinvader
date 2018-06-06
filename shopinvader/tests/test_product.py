# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import ProductCommonCase


class ProductCase(ProductCommonCase):

    def install_lang(self, lang_xml_id):
        lang = self.env.ref(lang_xml_id)
        wizard = self.env['base.language.install'].create({
            'lang': lang.code,
            })
        wizard.lang_install()
        return lang

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
    def test_variant_attributes(self):
        attr_dict = {'color': u'Black',
                     'wi-fi': u'2.4 GHz',
                     'memory': u'16 GB'}
        self.assertDictEqual(
            self.shopinvader_variant.variant_attributes, attr_dict)

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
             'based_on': 'variant_attribute',
             'attribute_id': attribute_id.id})
        self.assertEqual(
            filter_on_attr.display_name, 'variant_attributes.wi-fi')

    def test_product_price(self):
        self.assertEqual(
            self.shopinvader_variant.price,
            {'default': {'tax_included': True, 'value': 750.0}}
            )

    def test_category_child_with_one_lang(self):
        self.backend.bind_all_category()
        categ = self.env.ref('product.product_category_1')
        shopinvader_categ = categ.shopinvader_bind_ids
        self.assertEqual(len(shopinvader_categ), 1)
        self.assertEqual(len(shopinvader_categ.shopinvader_child_ids), 3)

    def test_category_child_with_two_lang(self):
        lang = self.install_lang('base.lang_fr')
        self.backend.lang_ids |= lang
        self.backend.bind_all_category()
        categ = self.env.ref('product.product_category_1')
        self.assertEqual(len(categ.shopinvader_bind_ids), 2)
        shopinvader_categ = categ.shopinvader_bind_ids[0]
        self.assertEqual(len(shopinvader_categ.shopinvader_child_ids), 3)
        for binding in categ.shopinvader_bind_ids:
            self.assertEqual(
                binding.shopinvader_parent_id.lang_id, binding.lang_id)
            if binding.lang_id.code == 'fr_FR':
                self.assertEqual(binding.url_key, u'tous/en-vente')
            elif binding.lang_id.code == 'en_US':
                self.assertEqual(binding.url_key, u'all/saleable')

    def test_product_category_with_one_lang(self):
        self.backend.bind_all_product()
        product = self.env.ref('product.product_product_4')
        self.assertEqual(len(product.shopinvader_bind_ids), 1)
        shopinvader_product = product.shopinvader_bind_ids
        self.assertEqual(len(shopinvader_product.shopinvader_categ_ids), 3)

    def test_product_category_with_one_lang(self):
        lang = self.install_lang('base.lang_fr')
        self.backend.lang_ids |= lang
        self.backend.bind_all_category()
        self.backend.bind_all_product()
        product = self.env.ref('product.product_product_4')
        self.assertEqual(len(product.shopinvader_bind_ids), 2)
        shopinvader_product = product.shopinvader_bind_ids[0]
        self.assertEqual(len(shopinvader_product.shopinvader_categ_ids), 3)
        for binding in product.shopinvader_bind_ids:
            if binding.lang_id.code == 'fr_FR':
                self.assertEqual(binding.url_key, u'ipad-avec-ecran-retina')
            elif binding.lang_id.code == 'en_US':
                self.assertEqual(binding.url_key, u'ipad-retina-display')
