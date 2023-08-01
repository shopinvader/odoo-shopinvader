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
