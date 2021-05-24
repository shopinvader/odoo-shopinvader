# Copyright 2021 Camptocamp (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_test_helper import FakeModelLoader

from odoo import fields, models
from odoo.tests import SavepointCase

from odoo.addons.shopinvader.tests.common import _install_lang_odoo


class BackendCaseBase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Load fake models ->/
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from odoo.addons.connector_search_engine.tests.models import SeBackendFake

        class AgnosticBinding(models.Model):
            # `aaa` to keep it on top when sorting ;)
            _name = "shopinvader.aaa.test.agnostic.binding"
            _inherit = "se.binding"
            _se_index_lang_agnostic = True

            name = fields.Char()

        cls.AgnosticBinding = AgnosticBinding
        cls.loader.update_registry((SeBackendFake, AgnosticBinding))
        # ->/ Load fake models

        cls.se_backend = (
            cls.env[SeBackendFake._name].create({"name": "Fake SE"}).se_backend_id
        )
        cls.backend = cls.env.ref("shopinvader.backend_1")
        cls.backend.se_backend_id = cls.se_backend
        cls.prod_export = cls.env.ref("shopinvader.ir_exp_shopinvader_variant")
        cls.categ_export = cls.env.ref("shopinvader.ir_exp_shopinvader_category")
        cls.ir_model_model = cls.env["ir.model"]
        cls.variant_model = cls.ir_model_model._get("shopinvader.variant")
        cls.categ_model = cls.ir_model_model._get("shopinvader.category")
        cls.agnostic_model = cls.ir_model_model._get(cls.AgnosticBinding._name)
        cls.lang_en = cls.backend.lang_ids
        cls.lang_fr = _install_lang_odoo(cls.env, "base.lang_fr")

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()


class TestBackend(BackendCaseBase):
    def test_create_missing_indexes_1_lang(self):
        self.assertFalse(self.backend.index_ids)
        self.backend.action_add_missing_indexes()
        # AgnosticBinding does not generate any index since there's no export rec
        expected = [
            {
                "model_id": self.categ_model.id,
                "lang_id": self.lang_en.id,
                "exporter_id": self.categ_export.id,
            },
            {
                "model_id": self.variant_model.id,
                "lang_id": self.lang_en.id,
                "exporter_id": self.prod_export.id,
            },
        ]
        indexes = self.backend.index_ids.sorted(lambda x: x.model_id.model)
        self.assertRecordValues(indexes, expected)

    def test_create_missing_indexes_2_langs(self):
        self.assertFalse(self.backend.index_ids)
        self.backend.lang_ids += self.lang_fr
        self.backend.action_add_missing_indexes()
        expected = [
            {
                "model_id": self.categ_model.id,
                "lang_id": self.lang_en.id,
                "exporter_id": self.categ_export.id,
            },
            {
                "model_id": self.categ_model.id,
                "lang_id": self.lang_fr.id,
                "exporter_id": self.categ_export.id,
            },
            {
                "model_id": self.variant_model.id,
                "lang_id": self.lang_en.id,
                "exporter_id": self.prod_export.id,
            },
            {
                "model_id": self.variant_model.id,
                "lang_id": self.lang_fr.id,
                "exporter_id": self.prod_export.id,
            },
        ]
        indexes = self.backend.index_ids.sorted(
            lambda x: (x.model_id.model, x.lang_id.code)
        )
        self.assertRecordValues(indexes, expected)

    def test_create_missing_indexes_2_langs_with_agnostic_index(self):
        self.assertTrue(self.env[self.AgnosticBinding._name]._se_index_lang_agnostic)
        export = self.env["ir.exports"].create(
            {"name": "Agnostic", "resource": self.AgnosticBinding._name}
        )
        self.assertFalse(self.backend.index_ids)
        self.backend.lang_ids += self.lang_fr
        self.backend.action_add_missing_indexes()
        expected = [
            {
                "model_id": self.agnostic_model.id,
                "lang_id": False,
                "exporter_id": export.id,
            },
            {
                "model_id": self.categ_model.id,
                "lang_id": self.lang_en.id,
                "exporter_id": self.categ_export.id,
            },
            {
                "model_id": self.categ_model.id,
                "lang_id": self.lang_fr.id,
                "exporter_id": self.categ_export.id,
            },
            {
                "model_id": self.variant_model.id,
                "lang_id": self.lang_en.id,
                "exporter_id": self.prod_export.id,
            },
            {
                "model_id": self.variant_model.id,
                "lang_id": self.lang_fr.id,
                "exporter_id": self.prod_export.id,
            },
        ]
        indexes = self.backend.index_ids.sorted(
            lambda x: (x.model_id.model, x.lang_id.code)
        )
        self.assertRecordValues(indexes, expected)
