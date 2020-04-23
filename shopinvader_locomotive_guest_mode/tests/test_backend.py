# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo.addons.shopinvader_locomotive.tests.common import LocoCommonCase
from odoo.addons.shopinvader_locomotive.tests.test_backend import mock_site_api


class TestBackend(LocoCommonCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        # simplified version of site data
        self.site = {
            "name": "My site",
            "handle": "my-website-1",
            "_id": "space_id",
            "metafields": json.dumps({"foo": "test", "_store": {}}),
        }

    def test_synchronize_metadata(self):
        with mock_site_api(self.base_url, self.site) as mock:
            self.backend.synchronize_metadata()
            metafields = mock.request_history[0].json()["site"]["metafields"]
            store = json.loads(metafields)["_store"]
            self.assertIn("is_guest_mode_allowed", store)
            self.assertEqual(store["is_guest_mode_allowed"], "false")
        self.backend.is_guest_mode_allowed = True
        with mock_site_api(self.base_url, self.site) as mock:
            self.backend.synchronize_metadata()
            metafields = mock.request_history[0].json()["site"]["metafields"]
            store = json.loads(metafields)["_store"]
            self.assertIn("is_guest_mode_allowed", store)
            self.assertEqual(store["is_guest_mode_allowed"], "true")
