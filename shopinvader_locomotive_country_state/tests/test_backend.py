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
        country_us_id = ref("base.us")
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
                "allowed_country_ids": [(6, 0, country_us_id.ids)],
                "allowed_country_state_ids": [
                    (6, 0, country_us_id.state_ids[:-1].ids)
                ],
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
        with mock_site_api(self.base_url, self.site) as mock:
            self.backend.synchronize_metadata()
            metafields = self._extract_metafields(
                mock.request_history[0].json()["site"]["metafields"]
            )
            expected_available_countries = {
                "en": [
                    {
                        "name": country.name,
                        "id": country.id,
                        "states": [
                            {
                                "id": state.id,
                                "name": state.name,
                                "code": state.code,
                            }
                            for state in self.backend.allowed_country_state_ids.filtered(
                                lambda x: x.country_id == country
                            )
                        ],
                    }
                    for country in self.backend.allowed_country_ids
                ]
            }
            sorted_metafields_allowed_country_states = sorted(
                json.loads(metafields["_store"]["available_countries"])["en"][
                    0
                ]["states"],
                key=lambda x: x["id"],
            )
            sorted_expected_available_country_states = sorted(
                expected_available_countries["en"][0]["states"],
                key=lambda x: x["id"],
            )
            self.assertEquals(
                sorted_metafields_allowed_country_states,
                sorted_expected_available_country_states,
            )
