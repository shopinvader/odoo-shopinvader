# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from uuid import uuid4
from random import randint
import mock
from odoo import api, models
from odoo.fields import first
from odoo.addons.connector_search_engine.tests.common import TestSeBackendCase
from odoo.addons.queue_job.tests.common import JobMixin


class TestProductProduct(TestSeBackendCase, JobMixin):
    """
    Tests for product.product
    """

    def setUp(self):
        super(TestProductProduct, self).setUp()
        self.shopinvader_backend = self.env.ref('shopinvader.backend_1')
        self.shopinvader_backend.write({
            'se_backend_id': self.se_backend.se_backend_id.id,
        })
        self.product = self.env.ref('product.product_product_4')
        ref = self.env.ref
        self.index = self.env['se.index'].create({
            'name': 'test-product-index',
            'backend_id': self.se_backend.se_backend_id.id,
            'exporter_id': ref('shopinvader.ir_exp_shopinvader_variant').id,
            'lang_id': ref('base.lang_en').id,
            'model_id': ref('shopinvader.model_shopinvader_variant').id,
            })
        self.shopinvader_backend.bind_all_product()

    def _add_stock_to_product(self, product, qty=10):
        """
        Set the stock quantity of the product
        :param product: product.product recordset
        :param qty: float
        """
        wizard = self.env['stock.change.product.qty'].create({
            'product_id': product.id,
            'new_quantity': qty,
        })
        wizard.change_product_qty()

    def test_update_qty_from_wizard(self):
        """
        Test that updating the quantity through an inventory create a
        new queue.job
        """
        job = self.job_counter()
        self._add_stock_to_product(self.product, 100)
        self.assertEqual(job.count_created(), 1)

    def test_update_stock_on_new_product(self):
        """
        Recomputing binding which have been not exported yet, do nothing
        """
        self.assertEqual(self.product.shopinvader_bind_ids.sync_state, 'new')
        self.product._product_stock_update_all()
        self.assertEqual(self.product.shopinvader_bind_ids.data, {})

    def _test_update_stock_with_key(self, key_stock):
        shopinvader_product = self.product.shopinvader_bind_ids
        shopinvader_product.recompute_json()
        shopinvader_product.sync_state = 'to_update'
        self.assertEqual(
            shopinvader_product.data[key_stock],
            {u'global': {u'qty': 0.0}})

        jobs = self.job_counter()
        self._add_stock_to_product(self.product, 100)
        self.assertEqual(jobs.count_created(), 1)
        self.perform_jobs(jobs)

        self.assertEqual(
            shopinvader_product.data[key_stock],
            {u'global': {u'qty': 100.0}})

    def test_update_stock(self):
        """
        Recomputing product should update binding
        """
        self._test_update_stock_with_key('stock')

    def test_update_stock_with_special_key(self):
        """
        Recomputing product should update binding
        using the custom key defined by the user
        """
        export_line = self.env.ref(
            'shopinvader_product_stock.'
            'ir_exp_shopinvader_variant_stock_data')
        export_line.alias = 'stock_data:custom_stock'
        self._test_update_stock_with_key('custom_stock')

    def test_update_stock_without_alias(self):
        """
        Recomputing product should update binding
        Using the name as key
        """
        export_line = self.env.ref(
            'shopinvader_product_stock.'
            'ir_exp_shopinvader_variant_stock_data')
        export_line.alias = None
        self._test_update_stock_with_key('stock_data')

    def test_update_stock_without_key(self):
        """
        Recomputing product should update binding
        Without export line
        """
        export_line = self.env.ref(
            'shopinvader_product_stock.'
            'ir_exp_shopinvader_variant_stock_data')
        export_line.unlink()

        shopinvader_product = self.product.shopinvader_bind_ids
        shopinvader_product.recompute_json()
        shopinvader_product.sync_state = 'to_update'
        self.assertNotIn('stock', shopinvader_product.data)

        jobs = self.job_counter()
        self._add_stock_to_product(self.product, 100)
        self.assertEqual(jobs.count_created(), 1)
        self.perform_jobs(jobs)
        self.assertNotIn('stock', shopinvader_product.data)
