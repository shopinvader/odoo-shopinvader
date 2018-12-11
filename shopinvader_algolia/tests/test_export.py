# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.connector_algolia.tests.common import (
    mock_api,
    ConnectorAlgoliaCase)
import logging
from odoo.addons.queue_job.tests.common import JobMixin

_logger = logging.getLogger(__name__)


class TestExport(ConnectorAlgoliaCase, JobMixin):

    @classmethod
    def setUpClass(cls):
        super(TestExport, cls).setUpClass()
        cls.shopinvader_backend = cls.env.ref('shopinvader.backend_1')
        cls.shopinvader_backend.bind_all_product()
        cls.shopinvader_backend.bind_all_category()

    def setUp(self):
        super(TestExport, self).setUp()
        self.index_product = self.env.ref('shopinvader_algolia.index_1')
        self.index_categ = self.env.ref('shopinvader_algolia.index_2')

    def test_10_export_one_product(self):
        product = self.env.ref('product.product_product_3_product_template')
        si_variant = product.shopinvader_bind_ids[0].shopinvader_variant_ids[0]
        with mock_api(self.env) as mocked_api:
            si_variant.recompute_json()
            si_variant.export()
            self.assertTrue('demo_algolia_backend_shopinvader_variant_en_US' in mocked_api.index)
        index = mocked_api.index['demo_algolia_backend_shopinvader_variant_en_US']
        self.assertEqual(1, len(index._calls))
        method, values = index._calls[0]
        self.assertEqual('add_objects', method)
        self.assertEqual(
            1, len(values), "Only one shopinvader variant should be exported")
        value = values[0]
        self.assertEqual(
            value['model']['name'], si_variant.product_tmpl_id.name)
        self.assertEqual(value['objectID'], product.id)
        self.assertEqual(value['sku'], si_variant.default_code)

    def test_20_recompute_all_products(self):
        bindings = self.env['shopinvader.variant'].search([])
        for binding in bindings:
            self.assertEqual(binding.data, {})
        jobs = self.job_counter()
        self.index_product.recompute_all_binding()
        self.assertEqual(jobs.count_created(), len(bindings))
        self.perform_jobs(jobs)
        for binding in bindings:
            self.assertEqual(binding.data['objectID'], binding.record_id.id)

    def _test_export_all_binding(self, index):
        init_jobs = self.job_counter()
        index.recompute_all_binding()
        self.perform_jobs(init_jobs)
        count = self.env[index.model_id.model].search_count([])

        jobs = self.job_counter()
        index.batch_export()
        self.assertEqual(jobs.count_created(), 1)
        with mock_api(self.env) as mocked_api:
            self.perform_jobs(jobs)
        self.assertTrue(index.name in mocked_api.index)
        index_api = mocked_api.index[index.name]
        self.assertEqual(
            1, len(index_api._calls),
            "All bindings must be exported in 1 call")
        method, values = index_api._calls[0]
        self.assertEqual('add_objects', method)
        self.assertEqual(
            count, len(values), "All bindings should be exported")

    def test_20_export_all_products(self):
        self._test_export_all_binding(self.index_product)

    def test_30_export_all_categories(self):
        self._test_export_all_binding(self.index_categ)
