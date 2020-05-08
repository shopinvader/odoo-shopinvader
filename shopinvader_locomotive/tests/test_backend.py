# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging
from contextlib import contextmanager

from .common import LocoCommonCase

_logger = logging.getLogger(__name__)

# pylint: disable=W7936
try:
    import requests_mock
except (ImportError, IOError) as err:
    _logger.debug(err)

ODOO_STORE_JSON_KEY = ["all_filters", "available_countries", "currencies_rate"]


@contextmanager
def mock_site_api(base_url, site):
    with requests_mock.mock() as m:
        m.post(base_url + "/tokens.json", json={"token": u"744cfcfb3cd3"})
        m.get(base_url + "/sites", json=[site])
        yield m.put(
            base_url + "/sites/%s" % site["_id"],
            json={"foo": "we_do_not_care"},
        )


class TestBackend(LocoCommonCase):
    def setUp(self, *args, **kwargs):
        super(TestBackend, self).setUp(*args, **kwargs)
        ref = self.env.ref
        country_ids = [ref("base.fr").id, ref("base.us").id]
        filter_ids = [
            ref("shopinvader.product_filter_1").id,
            ref("shopinvader.product_filter_2").id,
        ]
        currency_ids = [ref("base.USD").id, ref("base.EUR").id]
        self.backend.write(
            {
                "allowed_country_ids": [(6, 0, country_ids)],
                "filter_ids": [(6, 0, filter_ids)],
                "currency_ids": [(6, 0, currency_ids)],
            }
        )
        # simplified version of site data
        self.site = {
            "name": "My site",
            "handle": "shopinvader",
            "_id": "space_id",
            "metafields": json.dumps(
                {
                    "foo": "test",
                    "_store": {
                        "bar": "test",
                        "all_filters": "{}",
                        "available_countries": "{}",
                    },
                }
            ),
        }

    def _extract_metafields(self, metafields):
        metafields = json.loads(metafields)
        self.assertIn("_store", metafields)
        for key, vals in metafields["_store"].items():
            if key in ODOO_STORE_JSON_KEY:
                self.assertIsInstance(vals, unicode)
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
                                "code": "variant_attributes.memory",
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
                },
            }
            self.assertEqual(metafields, expected_metafields)

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
                },
            }
            self.assertEqual(metafields, expected_metafields)
