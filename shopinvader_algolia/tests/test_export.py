# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.connector_algolia.tests.common import (
    mock_api,
    ConnectorAlgoliaCase)
import logging
from odoo import _
from odoo.addons.queue_job.job import Job

_logger = logging.getLogger(__name__)


class TestExport(ConnectorAlgoliaCase):

    @classmethod
    def setUpClass(cls):
        super(TestExport, cls).setUpClass()
        cls.shopinvader_backend = cls.env.ref('shopinvader.backend_1')
        cls.shopinvader_backend.bind_all_product()
        cls.shopinvader_backend.bind_all_category()

    def test_10_export_one_product(self):
        product = self.env.ref('product.product_product_3_product_template')
        si_variant = product.shopinvader_bind_ids[0].shopinvader_variant_ids[0]
        with mock_api(self.env) as mocked_api:
            si_variant._scheduler_export(
                domain=[('id', '=', si_variant.id)], delay=False)
            self.assertTrue('algolia-product' in mocked_api.index)
        index = mocked_api.index['algolia-product']
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

    def test_20_export_all_products(self):
        queue_job = self.env['queue.job']
        existing_jobs = queue_job.search([])
        # a job is created to export all products
        self.shopinvader_backend.export_all_product()
        new_jobs = queue_job.search([])
        new_job = new_jobs - existing_jobs
        self.assertEqual(1, len(new_job))
        job = Job.load(self.env, new_job.uuid)
        self.assertEqual(
            _('Prepare a batch export of indexes'),
            job.description)
        existing_jobs = new_jobs
        # perform the job
        job.perform()
        new_jobs = queue_job.search([])
        new_job = new_jobs - existing_jobs
        self.assertEqual(1, len(new_job))
        job = Job.load(self.env, new_job.uuid)
        count = self.env['shopinvader.product'].search_count([])
        self.assertEqual(
            _("Export %d records of %d for index 'algolia-product'") % (
                count, count), job.description)
        # the last job is the one performing the export
        job = Job.load(self.env, new_job.uuid)
        with mock_api(self.env) as mocked_api:
            job.perform()
        self.assertTrue('algolia-product' in mocked_api.index)
        index = mocked_api.index['algolia-product']
        self.assertEqual(
            1, len(index._calls), "All variants must be exported in 1 call")
        method, values = index._calls[0]
        self.assertEqual('add_objects', method)
        self.assertEqual(
            count, len(values), "All variants should be exported")

    def test_30_export_all_categories(self):
        queue_job = self.env['queue.job']
        existing_jobs = queue_job.search([])
        # a job is created to export all products
        self.shopinvader_backend.export_all_category()
        new_jobs = queue_job.search([])
        new_job = new_jobs - existing_jobs
        self.assertEqual(1, len(new_job))
        job = Job.load(self.env, new_job.uuid)
        self.assertEqual(
            _('Prepare a batch export of indexes'),
            job.description)
        existing_jobs = new_jobs
        # perform the job
        job.perform()
        new_jobs = queue_job.search([])
        new_job = new_jobs - existing_jobs
        self.assertEqual(1, len(new_job))
        job = Job.load(self.env, new_job.uuid)
        count = self.env['shopinvader.category'].search_count([])
        self.assertEqual(
            _("Export %d records of %d for index 'algolia-category'") % (
                count, count),
            job.description)
        # the last job is the one performing the export
        job = Job.load(self.env, new_job.uuid)
        with mock_api(self.env) as mocked_api:
            job.perform()
        self.assertTrue('algolia-category' in mocked_api.index)
        index = mocked_api.index['algolia-category']
        self.assertEqual(
            1, len(index._calls), "All categories must be exported in 1 call")
        method, values = index._calls[0]
        self.assertEqual('add_objects', method)
        self.assertEqual(
            count, len(values), "All categories should be exported")
