# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from random import randint
from odoo.addons.connector_algolia.tests.common import ConnectorAlgoliaCase


class TestShopInvaderVariant(ConnectorAlgoliaCase):
    """
    Tests for shopinvader.variant
    """

    @classmethod
    def setUpClass(cls):
        super(TestShopInvaderVariant, cls).setUpClass()
        cls.shopinvader_backend = cls.env.ref('shopinvader.backend_1')
        cls.shopinvader_backend.bind_all_product()

    def setUp(self):
        super(TestShopInvaderVariant, self).setUp()
        self.index = self.env.ref('shopinvader_algolia.index_1')
        self.template = self.env.ref(
            'product.product_product_4_product_template')
        self.shopinvader_variants = self.env['shopinvader.variant'].search([
            ('record_id', 'in', self.template.product_variant_ids.ids),
            ('backend_id', '=', self.backend.id),
        ])
        self.stock_field = self.env.ref(
            "stock.field_product_product_qty_available")
        self.wizard_stock_obj = self.env['stock.change.product.qty']

    def _add_stock_to_product(self, product, qty=10):
        """
        Set the stock quantity of the product
        :param product: product.product recordset
        :param qty: float
        :return: bool
        """
        wizard_obj = self.wizard_stock_obj
        wizard = wizard_obj.create({
            'product_id': product.id,
            'new_quantity': qty,
        })
        wizard.change_product_qty()
        return True

    def test_export_json_stock1(self):
        """
        Test the export json created by the
        shopinvader.variant.json.export.mapper.
        This component should create a json who include the json saved
        into the json_akeneo field by adding every key/value into the result.
        For this case, we fill the json_akeneo field for every
        shopinvader_variant and then we check 1 by 1 if the value is correct.
        :return: bool
        """
        backend = self.backend
        index = self.index
        stock_field = self.stock_field
        backend.write({
            'product_stock_field_id': stock_field.id,
            'export_stock_key': 'stock_value',
        })
        shopinvader_variants = self.shopinvader_variants
        for product in shopinvader_variants.mapped("record_id"):
            qty = randint(2, 1000)
            self._add_stock_to_product(product, qty=qty)
        field_name = backend.product_stock_field_id.name
        stock_key = backend.export_stock_key
        with backend.work_on('shopinvader.variant', index=index) as work:
            mapper = work.component(usage='se.export.mapper')
            for shopinvader_variant in shopinvader_variants:
                stock_value = shopinvader_variant[field_name]
                map_record = mapper.map_record(shopinvader_variant)
                json_values = map_record.values()
                self.assertIn(stock_key, json_values.keys())
                self.assertEqual(stock_value, json_values.get(stock_key, 'a'))
        return True

    def test_export_json_stock2(self):
        """
        Test the export json created by the
        shopinvader.variant.json.export.mapper.
        This component should create a json who include the json saved
        into the json_akeneo field by adding every key/value into the result.
        For this case, we don't fill the export_stock_key to disable
        the stock export. So we ensure that it's not exported
        :return: bool
        """
        backend = self.backend
        index = self.index
        backend.write({
            'product_stock_field_id': False,
            'export_stock_key': False,
        })
        shopinvader_variants = self.shopinvader_variants
        for product in shopinvader_variants.mapped("record_id"):
            qty = randint(2, 1000)
            self._add_stock_to_product(product, qty=qty)
        with backend.work_on('shopinvader.variant', index=index) as work:
            mapper = work.component(usage='se.export.mapper')
            for shopinvader_variant in shopinvader_variants:
                map_record = mapper.map_record(shopinvader_variant)
                json_values = map_record.values()
                self.assertNotIn('stock_value', json_values.keys())
        return True
