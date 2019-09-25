# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from odoo.addons.shopinvader_locomotive.tests.common import (
    LocoCommonCase,
    mock_site_api,
)


class TestBackend(LocoCommonCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        self.metafields = {"elasticsearch": {}}
        # simplified version of site data
        self.site = {
            "name": "My site",
            "handle": "shopinvader",
            "_id": "space_id",
            "metafields": json.dumps(self.metafields),
        }
        self.routes = [
            [
                "*",
                {
                    "name": "category",
                    "template_handle": "category",
                    "index": "categories",
                },
            ],
            [
                "*",
                {
                    "name": "product",
                    "template_handle": "product",
                    "index": "products",
                },
            ],
        ]
        self.indices = [
            {
                "name": "categories",
                "index": "demo_elasticsearch_backend_shopinvader_category",
            },
            {
                "name": "products",
                "index": "demo_elasticsearch_backend_shopinvader_variant",
            },
        ]
        self.expected_elasticsearch_settings = {
            "indices": json.dumps(self.indices),
            "routes": json.dumps(self.routes),
            "url": self.backend.se_backend_id.specific_backend.es_server_host,
        }

    def _update_site_metafields(self, key, values):
        self.metafields[key] = values
        self.site["metafields"] = json.dumps(self.metafields)

    def _extract_metafields(self, metafields):
        metafields = json.loads(metafields)
        self.assertIn("_store", metafields)
        return metafields

    def test_elasticsearch_synchronize_01(self):
        """
        Data:
            * elasticsearch data not filled into locomotive
        Test case:
            * synchronize metadata
        Expected result:
            * elasticsearch information is filled
        :return:
        """
        self._update_site_metafields("elasticsearch", {})
        with mock_site_api(self.base_url, self.site) as mock:
            self.backend.synchronize_metadata()
            metafields = self._extract_metafields(
                mock.request_history[0].json()["site"]["metafields"]
            )
            self.assertDictEqual(
                metafields["elasticsearch"],
                self.expected_elasticsearch_settings,
            )

    def test_elasticsearch_synchronize_02(self):
        """
        Data:
            * elasticsearch data filled into locomotive
        Test case:
            * synchronize metadata
        Expected result:
            * elasticsearch data not updated into locomotive
        :return:
        """
        elasticsearch_values = {
            "indices": "dummy indices",
            "routes": "dummy routes",
            "url": "http://elastic.dummy",
        }
        self._update_site_metafields("elasticsearch", elasticsearch_values)
        with mock_site_api(self.base_url, self.site) as mock:
            self.backend.synchronize_metadata()
            metafields = self._extract_metafields(
                mock.request_history[0].json()["site"]["metafields"]
            )
            self.assertDictEqual(
                metafields["elasticsearch"], elasticsearch_values
            )

    def test_elasticsearch_synchronize_03(self):
        """
        Data:
            * elasticsearch data filled into locomotive
        Test case:
            * force reset settings
        Expected result:
            * elasticsearch data updated into locomotive
        :return:
        """
        elasticsearch_values = {
            "indices": "dummy indices",
            "routes": "dummy routes",
        }
        self._update_site_metafields("elasticsearch", elasticsearch_values)
        with mock_site_api(self.base_url, self.site) as mock:
            self.backend.reset_site_settings()
            metafields = self._extract_metafields(
                mock.request_history[0].json()["site"]["metafields"]
            )
            self.assertDictEqual(
                metafields["elasticsearch"],
                self.expected_elasticsearch_settings,
            )
