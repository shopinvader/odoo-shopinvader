# Copyright 2020 ForgeFlow S.L. (http://www.forgeflow.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo.addons.shopinvader_locomotive.tests.common import (
    LocoCommonCase,
    mock_site_api,
)

ODOO_STORE_JSON_KEY = [
    "all_filters",
    "available_countries",
    "currencies_rate",
    "locale_mapping",
    "available_customer_titles",
    "available_customer_industries",
    "available_country_states",
]


class TestBackend(LocoCommonCase):

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        super(TestBackend, cls).setUpClass()
        ref = cls.env.ref
        cls.odoo_url = cls.env["ir.config_parameter"].get_param("web.base.url")
        cls.api_url = "{}/shopinvader".format(cls.odoo_url)
        country_ids = [ref("base.us").id]
        state_ids = (
            cls.env["res.country.state"]
            .search([("country_id", "in", country_ids)])
            .ids
        )
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
                "allowed_country_state_ids": [(6, 0, state_ids)],
            }
        )

    def setUp(self):
        super(TestBackend, self).setUp()
        self.metafields = {
            "foo": "test",
            "_store": {"allowed_country_state_ids": {}},
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

    def _extract_metafields(self, metafields):
        metafields = json.loads(metafields)
        self.assertIn("_store", metafields)
        for key, vals in metafields["_store"].items():
            if key in "ODOO_STORE_JSON_KEY":
                self.assertIsInstance(vals, str)
                metafields["_store"][key] = json.loads(vals)
        return metafields

    def test_synchronize_country_state_metadata(self):
        ref = self.env.ref
        with mock_site_api(self.base_url, self.site) as mock:
            self.backend.synchronize_metadata()
            metafields = self._extract_metafields(
                mock.request_history[0].json()["site"]["metafields"]
            )
            expected_available_country_states = {
                "en": [
                    {
                        "id": ref("base.state_us_1").id,
                        "name": "Alabama",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_2").id,
                        "name": "Alaska",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_3").id,
                        "name": "Arizona",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_4").id,
                        "name": "Arkansas",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_5").id,
                        "name": "California",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_6").id,
                        "name": "Colorado",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_7").id,
                        "name": "Connecticut",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_8").id,
                        "name": "Delaware",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_9").id,
                        "name": "District of Columbia",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_10").id,
                        "name": "Florida",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_11").id,
                        "name": "Georgia",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_12").id,
                        "name": "Hawaii",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_13").id,
                        "name": "Idaho",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_14").id,
                        "name": "Illinois",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_15").id,
                        "name": "Indiana",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_16").id,
                        "name": "Iowa",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_17").id,
                        "name": "Kansas",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_18").id,
                        "name": "Kentucky",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_19").id,
                        "name": "Louisiana",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_20").id,
                        "name": "Maine",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_21").id,
                        "name": "Montana",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_22").id,
                        "name": "Nebraska",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_23").id,
                        "name": "Nevada",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_24").id,
                        "name": "New Hampshire",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_25").id,
                        "name": "New Jersey",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_26").id,
                        "name": "New Mexico",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_27").id,
                        "name": "New York",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_28").id,
                        "name": "North Carolina",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_29").id,
                        "name": "North Dakota",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_30").id,
                        "name": "Ohio",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_31").id,
                        "name": "Oklahoma",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_32").id,
                        "name": "Oregon",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_33").id,
                        "name": "Maryland",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_34").id,
                        "name": "Massachusetts",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_35").id,
                        "name": "Michigan",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_36").id,
                        "name": "Minnesota",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_37").id,
                        "name": "Mississippi",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_38").id,
                        "name": "Missouri",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_39").id,
                        "name": "Pennsylvania",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_40").id,
                        "name": "Rhode Island",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_41").id,
                        "name": "South Carolina",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_42").id,
                        "name": "South Dakota",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_43").id,
                        "name": "Tennessee",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_44").id,
                        "name": "Texas",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_45").id,
                        "name": "Utah",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_46").id,
                        "name": "Vermont",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_47").id,
                        "name": "Virginia",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_48").id,
                        "name": "Washington",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_49").id,
                        "name": "West Virginia",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_50").id,
                        "name": "Wisconsin",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_51").id,
                        "name": "Wyoming",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_as").id,
                        "name": "American Samoa",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_fm").id,
                        "name": "Federated States of Micronesia",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_gu").id,
                        "name": "Guam",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_mh").id,
                        "name": "Marshall Islands",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_mp").id,
                        "name": "Northern Mariana Islands",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_pw").id,
                        "name": "Palau",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_pr").id,
                        "name": "Puerto Rico",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_vi").id,
                        "name": "Virgin Islands",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_aa").id,
                        "name": "Armed Forces Americas",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_ae").id,
                        "name": "Armed Forces Europe",
                        "country_id": {"id": ref("base.us").id},
                    },
                    {
                        "id": ref("base.state_us_ap").id,
                        "name": "Armed Forces Pacific",
                        "country_id": {"id": ref("base.us").id},
                    },
                ]
            }
            sorted_metafields_allowed_country_states = sorted(
                json.loads(metafields["_store"]["available_country_states"])[
                    "en"
                ],
                key=lambda x: x["id"],
            )
            sorted_expected_available_country_states = sorted(
                expected_available_country_states["en"], key=lambda x: x["id"]
            )
            self.assertEquals(
                sorted_metafields_allowed_country_states,
                sorted_expected_available_country_states,
            )
