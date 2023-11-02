# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo_test_helper import FakeModelLoader

from odoo.addons.connector_search_engine.tests.common import TestSeBackendCaseBase
from odoo.addons.extendable.tests.common import ExtendableMixin


class TestBindingIndexBase(TestSeBackendCaseBase, FakeModelLoader, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Load fake models ->/
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from odoo.addons.connector_search_engine.tests.models import (
            FakeSeAdapter,
            SeBackend,
        )

        cls.loader.update_registry([SeBackend])
        cls.binding_model = cls.env["se.binding"]
        cls.se_index_model = cls.env["se.index"]
        cls.backend_model = cls.env["se.backend"]
        cls.backend = cls.backend_model.create(
            {"name": "Fake SE", "tech_name": "fake_se", "backend_type": "fake"}
        )

        cls.se_adapter = FakeSeAdapter

        cls.init_extendable_registry()

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        cls.reset_extendable_registry()
        super().tearDownClass()


class TestCategoryBindingBase(TestBindingIndexBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setup_records()

    @classmethod
    def _prepare_index_values(cls, backend=None):
        backend = backend or cls.backend
        return {
            "name": "Category Index",
            "backend_id": backend.id,
            "model_id": cls.env["ir.model"]
            .search([("model", "=", "product.category")], limit=1)
            .id,
            "lang_id": cls.env.ref("base.lang_en").id,
            "serializer_type": "shopinvader_category_exports",
        }

    @classmethod
    def setup_records(cls, backend=None):
        backend = backend or cls.backend
        # create an index for category model
        cls.se_index = cls.se_index_model.create(cls._prepare_index_values(backend))
        # create a binding + category alltogether
        cls.category = cls.env["product.category"].create({"name": "Test category"})
        cls.category_binding = cls.category._add_to_index(cls.se_index)


class TestProductBindingMixin:
    @classmethod
    def _prepare_index_values(cls, tst_cls, backend=None):
        backend = backend or tst_cls.backend
        return {
            "name": "Product Index",
            "backend_id": backend.id,
            "model_id": tst_cls.env["ir.model"]
            .search([("model", "=", "product.product")], limit=1)
            .id,
            "lang_id": tst_cls.env.ref("base.lang_en").id,
            "serializer_type": "shopinvader_product_exports",
        }

    @classmethod
    def setup_records(cls, tst_cls, backend=None):
        backend = backend or tst_cls.backend
        # create an index for product model
        tst_cls.se_index = tst_cls.env["se.index"].create(
            cls._prepare_index_values(tst_cls, backend)
        )
        # create a binding + product alltogether
        tst_cls.product = tst_cls.env.ref(
            "shopinvader_product.product_product_chair_vortex_white"
        )
        tst_cls.product_binding = tst_cls.product._add_to_index(tst_cls.se_index)
        tst_cls.product_expected = {
            "id": tst_cls.product.id,
            "name": tst_cls.product.name,
        }


class TestProductBindingBase(TestBindingIndexBase, TestProductBindingMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        TestProductBindingMixin.setup_records(cls)
