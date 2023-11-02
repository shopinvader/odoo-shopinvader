# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo_test_helper import FakeModelLoader

from odoo.addons.connector_search_engine.tests.common import TestSeBackendCaseBase
from odoo.addons.extendable.tests.common import ExtendableMixin
from odoo.addons.fs_product_multi_media.tests.test_fs_product_multi_media import (
    TestFsProductMultiMedia,
)


class ProductMediaCase(TestFsProductMultiMedia, TestSeBackendCaseBase, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.init_extendable_registry()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from odoo.addons.connector_search_engine.tests.models import SeBackend, SeIndex

        cls.loader.update_registry(
            (
                SeIndex,
                SeBackend,
            )
        )
        cls.backend = cls.env["se.backend"].create(
            {"name": "Fake SE", "tech_name": "fake_se", "backend_type": "fake"}
        )
        cls.product_index = cls.env["se.index"].create(
            {
                "name": "product",
                "backend_id": cls.backend.id,
                "model_id": cls.env.ref("product.model_product_product").id,
                "serializer_type": "shopinvader_product_exports",
            }
        )
        cls.product_binding = cls.product_a._add_to_index(cls.product_index)

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        cls.reset_extendable_registry()
        super().tearDownClass()

    def _default_media(self, media):
        return {
            "name": media.media_id.name,
            "url": media.media_id.file.internal_url,
            "type": {
                "name": media.media_id.media_type_id.name,
                "code": media.media_id.media_type_id.code,
            },
            "sequence": media.sequence,
        }
