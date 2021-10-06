# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader.tests.common import CommonCase

ES_CONFIG_US = {
    "elasticsearch": {
        "host": "http://elastic:9200",
        "indexes": {
            "shopinvader.category": "demo_elasticsearch_backend_shopinvader_category_en_US",
            "shopinvader.variant": "demo_elasticsearch_backend_shopinvader_variant_en_US",
        },
    }
}


class TestSettingsService(CommonCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        with self.work_on_services(
            partner=self.env.ref("shopinvader.partner_1")
        ) as work:
            self.settings_service = work.component(usage="settings")

    def test_elasticsearch(self):
        res = self.settings_service.dispatch("get_es_settings")
        self.assertDictEqual(res, ES_CONFIG_US)

    def test_all(self):
        res = self.settings_service.dispatch("get_all")
        self.assertIn("elasticsearch", res)
        self.assertDictEqual(res["elasticsearch"], ES_CONFIG_US["elasticsearch"])
