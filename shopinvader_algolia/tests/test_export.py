# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
import os
import unittest
import time
from openerp.addons.connector.tests.common import mock_job_delay_to_direct
import logging

_logger = logging.getLogger(__name__)


try:
    import algoliasearch
except ImportError:
    _logger.debug('Can not import algoliasearch')


@unittest.skipUnless(
    os.environ.get('ALGOLIA_TEST') and os.environ.get('ALGOLIA_APP', '') and
    os.environ.get('ALGOLIA_API_KEY', ''),
    "Missing algolia connection environment variables")
class ExportCase(TransactionCase):

    def setUp(self):
        super(ExportCase, self).setUp()
        self.backend = self.env.ref('connector_locomotivecms.backend_1')
        self.se_backend = self.env.ref('connector_algolia.backend_1')
        self.se_backend.username = os.environ['ALGOLIA_APP']
        self.se_backend.password = os.environ['ALGOLIA_API_KEY']
        self.backend.bind_all_product()
        self.backend.bind_all_category()
        self.path = (
            'openerp.addons.shopinvader_algolia.unit.exporter.export_record')
        if os.environ.get('TRAVIS_JOB_NUMBER', False):
            for index in self.env['se.index'].search(
                    [('backend_id', '=', self.se_backend.id)]):
                index.name = '%s-%s' % (
                    os.environ['TRAVIS_JOB_NUMBER'].replace('.', '_'),
                    index.name)

    def test_10_export_one_product(self):
        product = self.env.ref('product.product_product_3_product_template')
        si_variant = product.shopinvader_bind_ids[0].shopinvader_variant_ids[0]
        with mock_job_delay_to_direct(self.path):
            si_variant._scheduler_export(domain=[('id', '=', si_variant.id)])
        # If someone else has a less ugly solution, I'm interrested.
        time.sleep(5)
        client = algoliasearch.client.Client(
            self.se_backend.username, self.se_backend.password)
        index = client.initIndex(si_variant.index_id.name)
        algolia_product = index.search(si_variant.name)
        self.assertEqual(algolia_product['nbHits'], 1)
        self.assertEqual(algolia_product['hits'][0]['name'], si_variant.name)
        self.assertEqual(
            int(algolia_product['hits'][0]['objectID']), product.id)
        self.assertEqual(
            algolia_product['hits'][0]['default_code'],
            si_variant.default_code)

    def test_20_export_all_products(self):
        with mock_job_delay_to_direct(self.path):
            self.backend.export_all_product()

    def test_30_export_all_categories(self):
        with mock_job_delay_to_direct(self.path):
            self.backend.export_all_category()
