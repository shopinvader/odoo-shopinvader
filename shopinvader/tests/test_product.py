# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import CommonCase


class ProductCase(CommonCase):

    def test_create_shopinvader_variant(self):
        template = self.env.ref('product.product_product_25_product_template')
        lang = self.env.ref('base.lang_en')
        self.env['shopinvader.product'].create({
            'record_id': template.id,
            'backend_id': self.backend.id,
            'lang_id': lang.id
            })
        shopinvader_variant = self.env['shopinvader.variant'].search([
            ('record_id', 'in', template.product_variant_ids.ids),
            ('backend_id', '=', self.backend.id)])
        self.assertEqual(len(template.product_variant_ids),
                         len(shopinvader_variant))
