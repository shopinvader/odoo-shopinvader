# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from odoo_test_helper import FakeModelLoader

from .common import LocoCommonCase, mock_site_api


class TestSiteSearchEngineExportBase(LocoCommonCase):

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        super(TestSiteSearchEngineExportBase, cls).setUpClass()
        cls._setup_search_engine()
        cls.routes = [
            [
                "*",
                {
                    "name": "category",
                    "template_handle": "category",
                    "index": "categories",
                },
            ],
            [
                "*",
                {
                    "name": "product",
                    "template_handle": "product",
                    "index": "products",
                },
            ],
        ]
        cls.indexes = [
            {"name": "categories", "index": "fake_se_shopinvader_category"},
            {"name": "products", "index": "fake_se_shopinvader_variant"},
        ]
        cls.expected_settings = {
            "indices": json.dumps(cls.indexes),
            "routes": json.dumps(cls.routes),
        }

    @classmethod
    def _setup_search_engine(cls):
        raise NotImplementedError()

    def setUp(self):
        super(TestSiteSearchEngineExportBase, self).setUp()
        self.metafields = {self.search_engine_name: {}}
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
        return metafields

    def _test_sync(self, expected, reset=False):
        with mock_site_api(self.base_url, self.site) as mock:
            if reset:
                self.backend.reset_site_settings()
            else:
                self.backend.synchronize_metadata()
            metafields = self._extract_metafields(
                mock.request_history[0].json()["site"]["metafields"]
            )
            self.assertDictEqual(metafields[self.search_engine_name], expected)


class TestSiteSearchEngineExport(TestSiteSearchEngineExportBase):
    @classmethod
    def _setup_search_engine(cls):
        # Load fake models ->/
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from odoo.addons.connector_search_engine.tests.models import SeBackendFake

        cls.loader.update_registry((SeBackendFake,))
        # ->/ Load fake models
        cls.se_backend = (
            cls.env[SeBackendFake._name].create({"name": "Fake SE"}).se_backend_id
        )
        cls.search_engine_name = cls.se_backend.search_engine_name
        cls.backend.se_backend_id = cls.se_backend
        cls.env["se.index"].create(
            {
                "backend_id": cls.backend.se_backend_id.id,
                "name": "index-product",
                "lang_id": cls.env.ref("base.lang_en").id,
                "model_id": cls.env.ref("shopinvader.model_shopinvader_variant").id,
                "exporter_id": cls.env.ref("shopinvader.ir_exp_shopinvader_variant").id,
            }
        )
        cls.env["se.index"].create(
            {
                "backend_id": cls.backend.se_backend_id.id,
                "name": "index-category",
                "lang_id": cls.env.ref("base.lang_en").id,
                "model_id": cls.env.ref("shopinvader.model_shopinvader_category").id,
                "exporter_id": cls.env.ref(
                    "shopinvader.ir_exp_shopinvader_category"
                ).id,
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super(TestSiteSearchEngineExport, cls).tearDownClass()

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
        old_values = {"indices": "foo", "routes": "baz"}
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
        old_values = {"indices": "foo", "routes": "baz"}
        # force this values in settings
        self._update_site_metafields(self.search_engine_name, old_values)
        # run sync w/ reset -> they are computed again
        self._test_sync(self.expected_settings, reset=True)
