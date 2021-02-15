# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from .common import LocoCommonCase, mock_site_api


class TestBackendCommonCase(LocoCommonCase):

    maxDiff = None

    ODOO_STORE_JSON_KEY = [
        "all_filters",
        "available_countries",
        "currencies_rate",
        "locale_mapping",
        "available_customer_titles",
        "available_customer_industries",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        super().setUp()
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
        self.site.update({"metafields": json.dumps(self.metafields)})

    def _update_site_metafields(self, key, values):
        self.metafields[key] = values
        self.site["metafields"] = json.dumps(self.metafields)

    def _extract_metafields(self, metafields):
        metafields = json.loads(metafields)
        self.assertIn("_store", metafields)
        for key, vals in metafields["_store"].items():
            if key in self.ODOO_STORE_JSON_KEY:
                self.assertIsInstance(vals, str)
                metafields["_store"][key] = json.loads(vals)
        return metafields


class TestBackend(TestBackendCommonCase):
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
                                        u"code": u"AA",
                                        u"name": u"Armed Forces Americas",
                                    },
                                    {
                                        u"code": u"AE",
                                        u"name": u"Armed Forces Europe",
                                    },
                                    {u"code": u"AK", u"name": u"Alaska"},
                                    {u"code": u"AL", u"name": u"Alabama"},
                                    {
                                        u"code": u"AP",
                                        u"name": u"Armed Forces Pacific",
                                    },
                                    {u"code": u"AR", u"name": u"Arkansas"},
                                    {
                                        u"code": u"AS",
                                        u"name": u"American Samoa",
                                    },
                                    {u"code": u"AZ", u"name": u"Arizona"},
                                    {u"code": u"CA", u"name": u"California"},
                                    {u"code": u"CO", u"name": u"Colorado"},
                                    {u"code": u"CT", u"name": u"Connecticut"},
                                    {
                                        u"code": u"DC",
                                        u"name": u"District of Columbia",
                                    },
                                    {u"code": u"DE", u"name": u"Delaware"},
                                    {u"code": u"FL", u"name": u"Florida"},
                                    {
                                        u"code": u"FM",
                                        u"name": u"Federated States of Micronesia",
                                    },
                                    {u"code": u"GA", u"name": u"Georgia"},
                                    {u"code": u"GU", u"name": u"Guam"},
                                    {u"code": u"HI", u"name": u"Hawaii"},
                                    {u"code": u"IA", u"name": u"Iowa"},
                                    {u"code": u"ID", u"name": u"Idaho"},
                                    {u"code": u"IL", u"name": u"Illinois"},
                                    {u"code": u"IN", u"name": u"Indiana"},
                                    {u"code": u"KS", u"name": u"Kansas"},
                                    {u"code": u"KY", u"name": u"Kentucky"},
                                    {u"code": u"LA", u"name": u"Louisiana"},
                                    {
                                        u"code": u"MA",
                                        u"name": u"Massachusetts",
                                    },
                                    {u"code": u"MD", u"name": u"Maryland"},
                                    {u"code": u"ME", u"name": u"Maine"},
                                    {
                                        u"code": u"MH",
                                        u"name": u"Marshall Islands",
                                    },
                                    {u"code": u"MI", u"name": u"Michigan"},
                                    {u"code": u"MN", u"name": u"Minnesota"},
                                    {u"code": u"MO", u"name": u"Missouri"},
                                    {
                                        u"code": u"MP",
                                        u"name": u"Northern Mariana Islands",
                                    },
                                    {u"code": u"MS", u"name": u"Mississippi"},
                                    {u"code": u"MT", u"name": u"Montana"},
                                    {
                                        u"code": u"NC",
                                        u"name": u"North Carolina",
                                    },
                                    {u"code": u"ND", u"name": u"North Dakota"},
                                    {u"code": u"NE", u"name": u"Nebraska"},
                                    {
                                        u"code": u"NH",
                                        u"name": u"New Hampshire",
                                    },
                                    {u"code": u"NJ", u"name": u"New Jersey"},
                                    {u"code": u"NM", u"name": u"New Mexico"},
                                    {u"code": u"NV", u"name": u"Nevada"},
                                    {u"code": u"NY", u"name": u"New York"},
                                    {u"code": u"OH", u"name": u"Ohio"},
                                    {u"code": u"OK", u"name": u"Oklahoma"},
                                    {u"code": u"OR", u"name": u"Oregon"},
                                    {u"code": u"PA", u"name": u"Pennsylvania"},
                                    {u"code": u"PR", u"name": u"Puerto Rico"},
                                    {u"code": u"PW", u"name": u"Palau"},
                                    {u"code": u"RI", u"name": u"Rhode Island"},
                                    {
                                        u"code": u"SC",
                                        u"name": u"South Carolina",
                                    },
                                    {u"code": u"SD", u"name": u"South Dakota"},
                                    {u"code": u"TN", u"name": u"Tennessee"},
                                    {u"code": u"TX", u"name": u"Texas"},
                                    {u"code": u"UT", u"name": u"Utah"},
                                    {u"code": u"VA", u"name": u"Virginia"},
                                    {
                                        u"code": u"VI",
                                        u"name": u"Virgin Islands",
                                    },
                                    {u"code": u"VT", u"name": u"Vermont"},
                                    {u"code": u"WA", u"name": u"Washington"},
                                    {u"code": u"WI", u"name": u"Wisconsin"},
                                    {
                                        u"code": u"WV",
                                        u"name": u"West Virginia",
                                    },
                                    {u"code": u"WY", u"name": u"Wyoming"},
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

    def test_erp_synchronize_04(self):
        """Test only visible filters are exported"""
        self.backend.filter_ids.filtered(
            lambda x: x.display_name == "variant_attributes.color"
        ).visible = False
        with mock_site_api(self.base_url, self.site) as mock:
            self.backend.synchronize_metadata()
            metafields = self._extract_metafields(
                mock.request_history[0].json()["site"]["metafields"]
            )
            expected_filters = {
                "en": [
                    {
                        "code": "variant_attributes.legs",
                        "name": "Memory",
                        "help": "<p>Memory of the product</p>",
                    },
                ]
            }
            self.assertDictEqual(metafields["_store"]["all_filters"], expected_filters)
