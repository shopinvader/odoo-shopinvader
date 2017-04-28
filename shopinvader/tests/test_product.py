# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import CommonCase


class ProductCase(CommonCase):

    def test_create_nosql_product(self):
        template = self.env.ref('product.product_product_25_product_template')
        nosql_backend = self.env.ref('connector_nosql_algolia.backend_1')
        lang = self.env.ref('base.lang_en')
        self.env['locomotive.product'].create({
            'record_id': template.id,
            'backend_id': self.backend.id,
            'lang_id': lang.id
            })
        nosql_products = self.env['nosql.product.product'].search([
            ('record_id', 'in', template.product_variant_ids.ids),
            ('backend_id', '=', nosql_backend.id)])
        self.assertEqual(len(template.product_variant_ids),
                         len(nosql_products))
        self.assertEqual(nosql_products[0].index_id.lang_id, lang)
