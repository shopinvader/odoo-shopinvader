# Copyright 2021 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.shopinvader_locomotive.tests.common import mock_site_api
from odoo.addons.shopinvader_locomotive.tests.test_backend import TestBackendCommonCase


class TestShopinvaderTags(TestBackendCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.seasonal_conf = cls.env["seasonal.config"].create(
            {"name": "Test shop seasonal conf"}
        )
        cls.backend.company_id.default_seasonal_config_id = cls.seasonal_conf

    def test_synchronize_metadata(self):
        with mock_site_api(self.base_url, self.site) as mock:
            self.backend.synchronize_metadata()
            metafields = self._extract_metafields(
                mock.request_history[0].json()["site"]["metafields"]
            )
            self.assertEqual(
                metafields["_store"]["default_seasonal_config_id"],
                str(self.seasonal_conf.id),
            )
