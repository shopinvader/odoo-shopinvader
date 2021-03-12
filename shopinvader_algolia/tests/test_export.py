# Copyright 2017 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import os

from odoo.addons.connector_algolia.components.adapter import AlgoliaAdapter
from odoo.addons.connector_search_engine.tests.test_all import (
    TestBindingIndexBase,
)
from odoo.addons.shopinvader.tests.common import _install_lang_odoo

try:
    from vcr_unittest import VCRMixin
except ImportError:
    VCRMixin = None


class TestAlgoliaBackend(VCRMixin, TestBindingIndexBase):

    DEFAULT_FACET_KEYS = [
        "categories.id",
        "Categories.lvl0hierarchical",
        "Categories.lvl1hierarchical",
        "Categories.lvl2hierarchical",
        "main",
        "redirect_url_key",
        "url_key",
        "sku",
        "price.default.value",
    ]

    @classmethod
    def setUpClass(cls):
        super(TestAlgoliaBackend, cls).setUpClass()
        AlgoliaAdapter._build_component(cls._components_registry)
        cls.backend_specific = cls.env.ref("connector_algolia.se_algolia_demo")
        cls.backend = cls.backend_specific.se_backend_id
        cls.backend_specific.algolia_app_id = os.environ.get(
            "ALGOLIA_APP_ID", "FAKE_APP"
        )
        cls.backend_specific.algolia_api_key = os.environ.get(
            "ALGOLIA_API_KEY", "FAKE_KEY"
        )
        cls.shopinvader_backend = cls.env.ref("shopinvader.backend_1")
        cls.shopinvader_backend.bind_all_product()
        cls.shopinvader_backend.bind_all_category()
        cls.index_product = cls.env.ref("shopinvader_algolia.index_1")
        cls.index_categ = cls.env.ref("shopinvader_algolia.index_2")
        cls.index_config = cls.env["se.index.config"].create(
            {"name": "Custom"}
        )
        cls.index_config.body = {
            "attributesForFaceting": ["whatever.you.search"]
        }
        cls.index_product.config_id = cls.index_config

    def _get_vcr_kwargs(self, **kwargs):
        return {
            "record_mode": "once",
            "match_on": ["method", "path", "query"],
            "filter_headers": ["Authorization"],
            "decode_compressed_response": True,
        }

    def setUp(self):
        super(TestAlgoliaBackend, self).setUp()
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
        self.assertEqual(len(self.requests), 1)
        request = self.requests[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(
            self.parse_path(request.uri),
            "/1/indexes/demo_algolia_backend_shopinvader_variant_en_US/batch",
        )
        request_data = json.loads(request.body.decode("utf-8"))["requests"]
        self.assertEqual(len(request_data), 1)
        self.assertEqual(request_data[0]["action"], "addObject")
        self.assertEqual(request_data[0]["body"], si_variant.data)

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

        self.assertEqual(len(self.requests), 1)
        request = self.requests[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(
            self.parse_path(request.uri), "/1/indexes/%s/batch" % index.name
        )
        request_data = json.loads(request.body.decode("utf-8"))["requests"]
        self.assertEqual(
            len(request_data), binding_nbr, "All bindings should be exported"
        )
        self.assertEqual(request_data[0]["action"], "addObject")

    def test_20_export_all_products(self):
        self._test_export_all_binding(self.index_product)

    def test_30_export_all_categories(self):
        self._test_export_all_binding(self.index_categ)

    def test_facet_settings(self):
        _install_lang_odoo(self.env, "base.lang_fr")
        filter1 = self.env.ref("shopinvader.product_filter_1")
        filter2 = self.env.ref("shopinvader.product_filter_2")
        attr1 = filter1.variant_attribute_id
        attr2 = filter2.variant_attribute_id
        attr1.with_context(lang="fr_FR").name = attr1.name + " FR"
        attr2.with_context(lang="fr_FR").name = attr2.name + " FR"
        self.shopinvader_backend.filter_ids = filter1 + filter2

        settings_en = self.env["shopinvader.variant"]._get_facetting_values(
            self.backend, self.env.ref("base.lang_en")
        )
        settings_fr = self.env["shopinvader.variant"]._get_facetting_values(
            self.backend, self.env.ref("base.lang_fr")
        )
        self.assertEqual(
            settings_en,
            self.DEFAULT_FACET_KEYS
            + ["variant_attributes.legs", "variant_attributes.color"],
        )
        self.assertEqual(
            settings_fr,
            self.DEFAULT_FACET_KEYS
            + ["variant_attributes.legs_fr", "variant_attributes.color_fr"],
        )

    def test_index_facet_settings_merge(self):
        # Settings from index config and from _get_facetting_values
        # should be merged together
        settings = self.index_product._get_settings()
        self.assertEqual(
            sorted(settings["attributesForFaceting"]),
            sorted(self.DEFAULT_FACET_KEYS + ["whatever.you.search"]),
        )
