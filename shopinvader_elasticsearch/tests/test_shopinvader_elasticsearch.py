# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from odoo.addons.connector_elasticsearch.components.adapter import (
    ElasticsearchAdapter,
)
from odoo.addons.connector_search_engine.tests.test_all import (
    TestBindingIndexBase,
)
from odoo.tools import mute_logger
from vcr_unittest import VCRMixin


class TestElasticsearchBackend(VCRMixin, TestBindingIndexBase):
    @classmethod
    @mute_logger("odoo.addons.product.models.product")
    def setUpClass(cls):
        super(TestElasticsearchBackend, cls).setUpClass()
        ElasticsearchAdapter._build_component(cls._components_registry)
        cls.backend_specific = cls.env.ref("connector_elasticsearch.backend_1")
        cls.backend = cls.backend_specific.se_backend_id
        cls.shopinvader_backend = cls.env.ref("shopinvader.backend_1")
        cls.shopinvader_backend.bind_all_product()
        cls.shopinvader_backend.bind_all_category()
        cls.index_product = cls.env.ref("shopinvader_elasticsearch.index_1")
        cls.index_categ = cls.env.ref("shopinvader_elasticsearch.index_2")

    def _get_vcr_kwargs(self, **kwargs):
        return {
            "record_mode": "once",
            "match_on": ["method", "path", "query"],
            "filter_headers": ["Authorization"],
            "decode_compressed_response": True,
        }

    def setUp(self):
        super(TestElasticsearchBackend, self).setUp()
        if self.vcr_enabled:
            # TODO we should discuss about this
            # @laurent @simone @guewen
            # testing what we have in self.cassette.request
            # is maybe not a good idea as the contain tested is the
            # recorded contain and not the request done
            # this hack give store the real request in requests
            # maybe we should propose such helper in vcr-unitest?
            self.requests = []
            original = self.cassette.play_response

            def play_response(request):
                self.requests.append(request)
                return original(request)

            self.cassette.play_response = play_response

    def test_10_export_one_product(self):
        product = self.env.ref("product.product_product_3_product_template")
        si_variant = product.shopinvader_bind_ids[0].shopinvader_variant_ids[0]
        si_variant.recompute_json()
        si_variant.synchronize()
        self.assertTrue(len(self.requests))
        request = self.requests[-1]
        self.assertEqual(request.method, "POST")
        self.assertEqual(self.parse_path(request.uri), "/_bulk")
        # it's a bulk operation....
        # the first line should the reference to the elastic objetct (index)
        # the next line is for product info
        lines = list(filter(None, request.body.split(b"\n")))
        self.assertEqual(len(lines), 2)
        index_data = json.loads(lines[0].decode("utf-8"))
        product_data = json.loads(lines[1].decode("utf-8"))
        self.assertIn("index", index_data)
        self.assertEqual(
            index_data["index"]["_index"], self.index_product.name.lower()
        )
        self.assertEqual(index_data["index"]["_id"], si_variant.record_id.id)
        self.assertEqual(product_data, si_variant.data)

    @mute_logger("odoo.addons.product.models.product")
    def test_20_recompute_all_products(self):
        bindings = self.env["shopinvader.variant"].search([])
        bindings.write({"data": {}})
        self.index_product.recompute_all_binding()
        for binding in bindings:
            self.assertEqual(binding.data["objectID"], binding.record_id.id)

    def _test_export_all_binding(self, index):
        index.recompute_all_binding()
        index.batch_export()
        binding_nbr = self.env[index.model_id.model].search_count([])

        request = self.requests[-1]
        self.assertEqual(request.method, "POST")
        self.assertEqual(self.parse_path(request.uri), "/_bulk")
        # it's a bulk operation....
        # For eash operation we have:
        # a first line for the reference to the elastic object (index)
        # a second line for binding info
        lines = list(filter(None, request.body.split(b"\n")))
        self.assertEqual(len(lines), binding_nbr * 2)
        cpt = 0
        for line in lines:
            cpt += 1
            if cpt % 2 == 0:
                # product info
                continue
            # index info
            index_data = json.loads(line.decode("utf-8"))
            self.assertIn("index", index_data)
            self.assertEqual(index_data["index"]["_index"], index.name.lower())

    @mute_logger("odoo.addons.product.models.product")
    def test_20_export_all_products(self):
        self._test_export_all_binding(self.index_product)

    def test_30_export_all_categories(self):
        self._test_export_all_binding(self.index_categ)
