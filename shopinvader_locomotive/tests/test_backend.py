# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import LocoCommonCase
import json
import logging
_logger = logging.getLogger(__name__)

# pylint: disable=W7936
try:
    import requests_mock
except (ImportError, IOError) as err:
    _logger.debug(err)


class TestBackend(LocoCommonCase):

    def setUp(self, *args, **kwargs):
        super(TestBackend, self).setUp(*args, **kwargs)
        ref = self.env.ref
        country_ids = [ref('base.fr').id, ref('base.us').id]
        filter_ids = [
            ref('shopinvader.product_filter_1').id,
            ref('shopinvader.product_filter_2').id]
        self.backend.write({
            'allowed_country_ids': [(6, 0, country_ids)],
            'filter_ids': [(6, 0, filter_ids)],
            })
        self.site = {
            'name': 'My site',
            'handle': 'spacediscount',
            '_id': 'space_id',
            'metafields': json.dumps({
                'foo': 'test',
                '_store': {
                    'all_filters': '{}',
                    'available_countries': '{}',
                    },
                }),
            }

    def test_synchronize(self):
        # simplified version of site data
        with requests_mock.mock() as m:
            m.post(
                self.base_url + '/tokens.json',
                json={'token': u'744cfcfb3cd3'})
            m.get(
                self.base_url + '/sites',
                json=[self.site])
            put_mock = m.put(
                self.base_url + '/sites/%s' % self.site['_id'],
                json={'foo': 'we_do_not_care'})
            self.backend.synchronize_metadata()
            metafields = json.loads(
                put_mock.request_history[0].json()['site']['metafields'])
            self.assertIn('foo', metafields)
            self.assertIn('_store', metafields)
            self.assertIn('all_filters', metafields['_store'])
            all_filters = json.loads(metafields['_store']['all_filters'])
            self.assertEqual(
                all_filters,
                {
                    "en": [{
                        "code": "attributes.color",
                        "name": "Color",
                        "help": "<p>Color of the product</p>",
                        }, {
                        "code": "attributes.memory",
                        "name": "Memory",
                        "help": "<p>Memory of the product</p>",
                        }]
                })
            self.assertIn('available_countries', metafields['_store'])
            available_countries = json.loads(
                metafields['_store']['available_countries'])
            self.assertEqual(
                available_countries,
                {
                    "en": [
                        {"name": "France", "id": 76},
                        {"name": "United States", "id": 235},
                    ]
                })
