# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from .common import LocoCommonCase, mock_site_api

ODOO_STORE_JSON_KEY = [
    "all_filters",
    "available_countries",
    "currencies_rate",
    "locale_mapping",
]


class TestBackend(LocoCommonCase):

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        super(TestBackend, cls).setUpClass()
        ref = cls.env.ref
        cls.odoo_url = cls.env["ir.config_parameter"].get_param("web.base.url")
        cls.api_url = "{}/shopinvader".format(cls.odoo_url)
        country_ids = [ref("base.fr").id, ref("base.us").id]
        filter_ids = [
            ref("shopinvader.product_filter_1").id,
            ref("shopinvader.product_filter_2").id,
        ]
        currency_ids = [ref("base.USD").id, ref("base.EUR").id]
        cls.backend.write(
            {
                # Fix test demo data compat:
                # make sure no search backend is attached here.
                # This test suite tests only data unrelated from SE
                # and there might be some modules
                # (eg: shopinvader_elasticsearch)
                # that tie a specific backend to the main demo backend.
                "se_backend_id": False,
                # ---------------------
                "allowed_country_ids": [(6, 0, country_ids)],
                "filter_ids": [(6, 0, filter_ids)],
                "currency_ids": [(6, 0, currency_ids)],
            }
        )

    def setUp(self):
        super(TestBackend, self).setUp()
        self.metafields = {
            "foo": "test",
            "_store": {
                "bar": "test",
                "all_filters": "{}",
                "available_countries": "{}",
                "locale_mapping": "{}",
            },
            "erp": {
                "api_key": self.backend.auth_api_key_id.key,
                "api_url": self.api_url,
            },
        }
        # simplified version of site data
        self.site = {
            "name": "My site",
            "handle": "shopinvader",
            "_id": "space_id",
            "metafields": json.dumps(self.metafields),
        }

    def _update_site_metafields(self, key, values):
        self.metafields[key] = values
        self.site["metafields"] = json.dumps(self.metafields)

    def _extract_metafields(self, metafields):
        metafields = json.loads(metafields)
        self.assertIn("_store", metafields)
        for key, vals in metafields["_store"].items():
            if key in ODOO_STORE_JSON_KEY:
                self.assertIsInstance(vals, str)
                metafields["_store"][key] = json.loads(vals)
        return metafields

    def test_synchronize_metadata(self):
        ref = self.env.ref
        with mock_site_api(self.base_url, self.site) as mock:
            self.backend.synchronize_metadata()
            metafields = self._extract_metafields(
                mock.request_history[0].json()["site"]["metafields"]
            )
            expected_metafields = {
                "foo": "test",
                "_store": {
                    "bar": "test",
                    "all_filters": {
                        "en": [
                            {
                                "code": "variant_attributes.color",
                                "name": "Color",
                                "help": "<p>Color of the product</p>",
                            },
                            {
                                "code": "variant_attributes.legs",
                                "name": "Memory",
                                "help": "<p>Memory of the product</p>",
                            },
                        ]
                    },
                    "available_countries": {
                        "en": [
                            {"name": "France", "id": ref("base.fr").id},
                            {"name": "United States", "id": ref("base.us").id},
                        ]
                    },
                    "currencies_rate": {
                        "USD": ref("base.USD").rate,
                        "EUR": ref("base.EUR").rate,
                    },
                    "locale_mapping": {"en": "en_US"},
                },
                "erp": {
                    "api_key": self.backend.auth_api_key_id.key,
                    "api_url": self.api_url,
                },
            }
            self.assertDictEqual(metafields, expected_metafields)

    def test_synchronize_currency(self):
        ref = self.env.ref
        with mock_site_api(self.base_url, self.site) as mock:
            self.backend.synchronize_currency()
            metafields = self._extract_metafields(
                mock.request_history[0].json()["site"]["metafields"]
            )
            expected_metafields = {
                "foo": "test",
                "_store": {
                    "bar": "test",
                    "all_filters": {},
                    "available_countries": {},
                    "currencies_rate": {
                        "USD": ref("base.USD").rate,
                        "EUR": ref("base.EUR").rate,
                    },
                    "locale_mapping": {},
                },
                "erp": {
                    "api_key": self.backend.auth_api_key_id.key,
                    "api_url": self.api_url,
                },
            }
            self.assertDictEqual(metafields, expected_metafields)

    def test_erp_synchronize_01(self):
        """
        Data:
            * erp data not filled into locomotive
        Test case:
            * synchronize metadata
        Expected result:
            * erp information is filled
        :return:
        """
        self._update_site_metafields("erp", {})
        with mock_site_api(self.base_url, self.site) as mock:
            self.backend.synchronize_metadata()
            metafields = self._extract_metafields(
                mock.request_history[0].json()["site"]["metafields"]
            )
            self.assertDictEqual(
                metafields["erp"],
                {
                    "api_key": self.backend.auth_api_key_id.key,
                    "api_url": self.api_url,
                },
            )

    def test_erp_synchronize_02(self):
        """
        Data:
            * erp data filled into locomotive
        Test case:
            * synchronize metadata
        Expected result:
            * erp data not updated into locomotive
        :return:
        """
        erp_values = {"api_key": "dummy", "api_url": "https://dummy"}
        self._update_site_metafields("erp", erp_values)
        with mock_site_api(self.base_url, self.site) as mock:
            self.backend.synchronize_metadata()
            metafields = self._extract_metafields(
                mock.request_history[0].json()["site"]["metafields"]
            )
            self.assertDictEqual(metafields["erp"], erp_values)

    def test_erp_synchronize_03(self):
        """
        Data:
            * erp data filled into locomotive
        Test case:
            * force reset settings
        Expected result:
            * erp data updated into locomotive
        :return:
        """
        erp_values = {"api_key": "dummy", "api_url": "https://dummy"}
        self._update_site_metafields("erp", erp_values)
        with mock_site_api(self.base_url, self.site) as mock:
            self.backend.reset_site_settings()
            metafields = self._extract_metafields(
                mock.request_history[0].json()["site"]["metafields"]
            )
            self.assertDictEqual(
                metafields["erp"],
                {
                    "api_key": self.backend.auth_api_key_id.key,
                    "api_url": self.api_url,
                },
            )
