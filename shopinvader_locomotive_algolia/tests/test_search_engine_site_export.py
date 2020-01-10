# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from odoo.addons.shopinvader_locomotive import tests as base_tests

# black is not able to format this properly :/
Base = base_tests.test_search_engine_site_export.TestSiteSearchEngineExportBase


class TestSiteSearchEngineExport(Base):
    @classmethod
    def setUpClass(cls):
        super(TestSiteSearchEngineExport, cls).setUpClass()
        cls.indexes = [
            {
                "name": "categories",
                "index": "demo_algolia_backend_shopinvader_category",
            },
            {
                "name": "products",
                "index": "demo_algolia_backend_shopinvader_variant",
            },
        ]
        cls.expected_settings["indices"] = json.dumps(cls.indexes)
        cls.expected_settings["application_id"] = "ABCDEFG"
        cls.expected_settings["api_key"] = "123456789"

    @classmethod
    def _setup_search_engine(cls):
        cls.specific_backend = cls.env.ref("connector_algolia.se_algolia_demo")
        cls.specific_backend.write(
            {"algolia_app_id": "ABCDEFG", "algolia_api_key": "123456789"}
        )
        cls.backend.se_backend_id = cls.specific_backend.se_backend_id
        cls.search_engine_name = cls.backend.se_backend_id.search_engine_name

    def test_search_engine_synchronize_01(self):
        """
        Data:
            * SE data not filled into locomotive
        Test case:
            * synchronize metadata
        Expected result:
            * SE data is filled
        :return:
        """
        # wipe current settings
        self._update_site_metafields(self.search_engine_name, {})
        # run sync -> we get the expected default ones
        self._test_sync(self.expected_settings)

    def test_search_engine_synchronize_02(self):
        """
        Data:
            * SE data filled into locomotive
        Test case:
            * synchronize metadata
        Expected result:
            * SE data not updated into locomotive
        :return:
        """
        old_values = {
            "indices": "foo",
            "routes": "baz",
            "application_id": "REPLACE_ID",
            "api_key": "REPLACE_KEY",
        }
        # force this values in settings
        self._update_site_metafields(self.search_engine_name, old_values)
        # run sync w/no reset -> they are preserved
        self._test_sync(old_values)

    def test_search_engine_synchronize_03(self):
        """
        Data:
            * SE data filled into locomotive
        Test case:
            * force reset settings
        Expected result:
            * SE data updated into locomotive
        :return:
        """
        old_values = {
            "indices": "foo",
            "routes": "baz",
            "application_id": "REPLACE_ID",
            "api_key": "REPLACE_KEY",
        }
        # force this values in settings
        self._update_site_metafields(self.search_engine_name, old_values)
        # run sync w/ reset -> they are computed again
        self._test_sync(self.expected_settings, reset=True)
