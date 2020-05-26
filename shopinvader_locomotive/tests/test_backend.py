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
    "available_customer_titles",
    "available_customer_industries",
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
        title_ids = [
            ref("base.res_partner_title_miss").id,
            ref("base.res_partner_title_mister").id,
        ]
        industry_ids = [
            ref("base.res_partner_industry_A").id,
            ref("base.res_partner_industry_B").id,
        ]
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
                "partner_title_ids": [(6, 0, title_ids)],
                "partner_industry_ids": [(6, 0, industry_ids)],
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
                "available_customer_titles": "{}",
                "available_customer_industries": "{}",
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
        title_miss = ref("base.res_partner_title_miss")
        title_mister = ref("base.res_partner_title_mister")
        industry_a = ref("base.res_partner_industry_A")
        industry_b = ref("base.res_partner_industry_B")
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
                            {
                                "name": "France",
                                "id": ref("base.fr").id,
                                "states": [],
                            },
                            {
                                "name": "United States",
                                "id": ref("base.us").id,
                                "states": [
                                    {
                                        "id": ref("base.state_us_1").id,
                                        "name": "Alabama",
                                        "code": "AL",
                                    },
                                    {
                                        "id": ref("base.state_us_2").id,
                                        "name": "Alaska",
                                        "code": "AK",
                                    },
                                    {
                                        "id": ref("base.state_us_3").id,
                                        "name": "Arizona",
                                        "code": "AZ",
                                    },
                                    {
                                        "id": ref("base.state_us_4").id,
                                        "name": "Arkansas",
                                        "code": "AR",
                                    },
                                    {
                                        "id": ref("base.state_us_5").id,
                                        "name": "California",
                                        "code": "CA",
                                    },
                                    {
                                        "id": ref("base.state_us_6").id,
                                        "name": "Colorado",
                                        "code": "CO",
                                    },
                                    {
                                        "id": ref("base.state_us_7").id,
                                        "name": "Connecticut",
                                        "code": "CT",
                                    },
                                    {
                                        "id": ref("base.state_us_8").id,
                                        "name": "Delaware",
                                        "code": "DE",
                                    },
                                    {
                                        "id": ref("base.state_us_9").id,
                                        "name": "District of Columbia",
                                        "code": "DC",
                                    },
                                    {
                                        "id": ref("base.state_us_10").id,
                                        "name": "Florida",
                                        "code": "FL",
                                    },
                                    {
                                        "id": ref("base.state_us_11").id,
                                        "name": "Georgia",
                                        "code": "GA",
                                    },
                                    {
                                        "id": ref("base.state_us_12").id,
                                        "name": "Hawaii",
                                        "code": "HI",
                                    },
                                    {
                                        "id": ref("base.state_us_13").id,
                                        "name": "Idaho",
                                        "code": "ID",
                                    },
                                    {
                                        "id": ref("base.state_us_14").id,
                                        "name": "Illinois",
                                        "code": "IL",
                                    },
                                    {
                                        "id": ref("base.state_us_15").id,
                                        "name": "Indiana",
                                        "code": "IN",
                                    },
                                    {
                                        "id": ref("base.state_us_16").id,
                                        "name": "Iowa",
                                        "code": "IA",
                                    },
                                    {
                                        "id": ref("base.state_us_17").id,
                                        "name": "Kansas",
                                        "code": "KS",
                                    },
                                    {
                                        "id": ref("base.state_us_18").id,
                                        "name": "Kentucky",
                                        "code": "KY",
                                    },
                                    {
                                        "id": ref("base.state_us_19").id,
                                        "name": "Louisiana",
                                        "code": "LA",
                                    },
                                    {
                                        "id": ref("base.state_us_20").id,
                                        "name": "Maine",
                                        "code": "ME",
                                    },
                                    {
                                        "id": ref("base.state_us_21").id,
                                        "name": "Montana",
                                        "code": "MT",
                                    },
                                    {
                                        "id": ref("base.state_us_22").id,
                                        "name": "Nebraska",
                                        "code": "NE",
                                    },
                                    {
                                        "id": ref("base.state_us_23").id,
                                        "name": "Nevada",
                                        "code": "NV",
                                    },
                                    {
                                        "id": ref("base.state_us_24").id,
                                        "name": "New Hampshire",
                                        "code": "NH",
                                    },
                                    {
                                        "id": ref("base.state_us_25").id,
                                        "name": "New Jersey",
                                        "code": "NJ",
                                    },
                                    {
                                        "id": ref("base.state_us_26").id,
                                        "name": "New Mexico",
                                        "code": "NM",
                                    },
                                    {
                                        "id": ref("base.state_us_27").id,
                                        "name": "New York",
                                        "code": "NY",
                                    },
                                    {
                                        "id": ref("base.state_us_28").id,
                                        "name": "North Carolina",
                                        "code": "NC",
                                    },
                                    {
                                        "id": ref("base.state_us_29").id,
                                        "name": "North Dakota",
                                        "code": "ND",
                                    },
                                    {
                                        "id": ref("base.state_us_30").id,
                                        "name": "Ohio",
                                        "code": "OH",
                                    },
                                    {
                                        "id": ref("base.state_us_31").id,
                                        "name": "Oklahoma",
                                        "code": "OK",
                                    },
                                    {
                                        "id": ref("base.state_us_32").id,
                                        "name": "Oregon",
                                        "code": "OR",
                                    },
                                    {
                                        "id": ref("base.state_us_33").id,
                                        "name": "Maryland",
                                        "code": "MD",
                                    },
                                    {
                                        "id": ref("base.state_us_34").id,
                                        "name": "Massachusetts",
                                        "code": "MA",
                                    },
                                    {
                                        "id": ref("base.state_us_35").id,
                                        "name": "Michigan",
                                        "code": "MI",
                                    },
                                    {
                                        "id": ref("base.state_us_36").id,
                                        "name": "Minnesota",
                                        "code": "MN",
                                    },
                                    {
                                        "id": ref("base.state_us_37").id,
                                        "name": "Mississippi",
                                        "code": "MS",
                                    },
                                    {
                                        "id": ref("base.state_us_38").id,
                                        "name": "Missouri",
                                        "code": "MO",
                                    },
                                    {
                                        "id": ref("base.state_us_39").id,
                                        "name": "Pennsylvania",
                                        "code": "PA",
                                    },
                                    {
                                        "id": ref("base.state_us_40").id,
                                        "name": "Rhode Island",
                                        "code": "RI",
                                    },
                                    {
                                        "id": ref("base.state_us_41").id,
                                        "name": "South Carolina",
                                        "code": "SC",
                                    },
                                    {
                                        "id": ref("base.state_us_42").id,
                                        "name": "South Dakota",
                                        "code": "SD",
                                    },
                                    {
                                        "id": ref("base.state_us_43").id,
                                        "name": "Tennessee",
                                        "code": "TN",
                                    },
                                    {
                                        "id": ref("base.state_us_44").id,
                                        "name": "Texas",
                                        "code": "TX",
                                    },
                                    {
                                        "id": ref("base.state_us_45").id,
                                        "name": "Utah",
                                        "code": "UT",
                                    },
                                    {
                                        "id": ref("base.state_us_46").id,
                                        "name": "Vermont",
                                        "code": "VT",
                                    },
                                    {
                                        "id": ref("base.state_us_47").id,
                                        "name": "Virginia",
                                        "code": "VA",
                                    },
                                    {
                                        "id": ref("base.state_us_48").id,
                                        "name": "Washington",
                                        "code": "WA",
                                    },
                                    {
                                        "id": ref("base.state_us_49").id,
                                        "name": "West Virginia",
                                        "code": "WV",
                                    },
                                    {
                                        "id": ref("base.state_us_50").id,
                                        "name": "Wisconsin",
                                        "code": "WI",
                                    },
                                    {
                                        "id": ref("base.state_us_51").id,
                                        "name": "Wyoming",
                                        "code": "WY",
                                    },
                                    {
                                        "id": ref("base.state_us_as").id,
                                        "name": "American Samoa",
                                        "code": "AS",
                                    },
                                    {
                                        "id": ref("base.state_us_fm").id,
                                        "name": "Federated States of Micronesia",
                                        "code": "FM",
                                    },
                                    {
                                        "id": ref("base.state_us_gu").id,
                                        "name": "Guam",
                                        "code": "GU",
                                    },
                                    {
                                        "id": ref("base.state_us_mh").id,
                                        "name": "Marshall Islands",
                                        "code": "MH",
                                    },
                                    {
                                        "id": ref("base.state_us_mp").id,
                                        "name": "Northern Mariana Islands",
                                        "code": "MP",
                                    },
                                    {
                                        "id": ref("base.state_us_pw").id,
                                        "name": "Palau",
                                        "code": "PW",
                                    },
                                    {
                                        "id": ref("base.state_us_pr").id,
                                        "name": "Puerto Rico",
                                        "code": "PR",
                                    },
                                    {
                                        "id": ref("base.state_us_vi").id,
                                        "name": "Virgin Islands",
                                        "code": "VI",
                                    },
                                    {
                                        "id": ref("base.state_us_aa").id,
                                        "name": "Armed Forces Americas",
                                        "code": "AA",
                                    },
                                    {
                                        "id": ref("base.state_us_ae").id,
                                        "name": "Armed Forces Europe",
                                        "code": "AE",
                                    },
                                    {
                                        "id": ref("base.state_us_ap").id,
                                        "name": "Armed Forces Pacific",
                                        "code": "AP",
                                    },
                                ],
                            },
                        ]
                    },
                    "currencies_rate": {
                        "USD": ref("base.USD").rate,
                        "EUR": ref("base.EUR").rate,
                    },
                    "locale_mapping": {"en": "en_US"},
                    "available_customer_titles": {
                        "en": [
                            {
                                "name": title_miss.name,
                                "id": title_miss.id,
                                "shortcut": title_miss.shortcut,
                            },
                            {
                                "name": title_mister.name,
                                "id": title_mister.id,
                                "shortcut": title_mister.shortcut,
                            },
                        ]
                    },
                    "available_customer_industries": {
                        "en": [
                            {
                                "name": industry_a.name,
                                "id": industry_a.id,
                                "full_name": industry_a.full_name,
                            },
                            {
                                "name": industry_b.name,
                                "id": industry_b.id,
                                "full_name": industry_b.full_name,
                            },
                        ]
                    },
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
                    "available_customer_titles": {},
                    "available_customer_industries": {},
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
