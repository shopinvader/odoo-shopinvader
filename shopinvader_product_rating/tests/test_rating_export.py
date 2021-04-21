# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.connector_search_engine.tests.test_all import TestBindingIndexBaseFake
from odoo.addons.shopinvader.tests.common import UtilsMixin
from odoo.addons.shopinvader_rating_abstract.tests.common import CommonRatingCase


class ExportRatingCase(TestBindingIndexBaseFake, CommonRatingCase, UtilsMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ref = cls.env.ref
        cls.index = cls.env["se.index"].create(
            {
                "name": "test-product-index",
                "backend_id": cls.backend_specific.se_backend_id.id,
                "exporter_id": ref("shopinvader.ir_exp_shopinvader_variant").id,
                "lang_id": ref("base.lang_en").id,
                "model_id": ref("shopinvader.model_shopinvader_variant").id,
            }
        )
        cls.backend = cls.env.ref("shopinvader.backend_1")
        cls.backend.write({"se_backend_id": cls.backend_specific.se_backend_id.id})

    def test_export(self):
        self._bind_products(self.product1, backend=self.backend)
        variant = self.env["shopinvader.variant"].search(
            [("record_id", "=", self.params["res_id"])], limit=1
        )
        rating = self.env["rating.rating"].create(self.params)
        variant.record_id.invalidate_cache()
        variant.recompute_json()
        rating.synchronize_rating()
        self.assertTrue(len(variant.data["ratings"]))
        self.assertEqual(variant.data["rating_stats"]["total"], 1)
