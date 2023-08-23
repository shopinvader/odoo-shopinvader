# Copyright 2021 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.tests.common import ComponentRegistryCase
from odoo.addons.shopinvader_restapi.tests.common import UtilsMixin
from odoo.addons.shopinvader_search_engine.tests.test_backend import BackendCaseBase


class TestProductSeasonalityCaseBase(
    BackendCaseBase, UtilsMixin, ComponentRegistryCase
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ComponentRegistryCase._setup_registry(cls)
        cls._load_module_components(cls, "shopinvader_product_seasonality")
        cls._load_module_components(
            cls, "shopinvader_product_seasonality_search_engine"
        )
        cls.seasonal_conf = cls.env["seasonal.config"].create(
            {
                "name": "Test seasonal conf",
            }
        )
        cls.backend._add_missing_indexes()
        cls.prod = cls.env.ref("product.product_product_2")

    def _create_line(self, **kw):
        vals = {
            "seasonal_config_id": self.seasonal_conf.id,
            "date_start": "2021-05-10",
            "date_end": "2021-05-16",
            "monday": True,
            "tuesday": True,
            "product_template_id": self.prod.product_tmpl_id.id,
            "product_id": self.prod.id,
            "backend_id": self.backend.id,
        }
        vals.update(kw)
        return self.env["shopinvader.seasonal.config.line"].create(vals)


class TestProductSeasonalityCaseNoJobs(TestProductSeasonalityCaseBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, test_queue_job_no_delay=True))

    def test_no_index(self):
        self.backend.index_ids.unlink()
        s_line = self._create_line()
        # There's no index on the backend yet
        self.assertFalse(s_line.index_id)

    def test_index(self):
        index = self.backend.index_ids.filtered(
            lambda x: x.model_id.model == "shopinvader.seasonal.config.line"
        )
        self.assertTrue(index)
        s_line = self._create_line()
        # There's no index on the backend yet
        self.assertEqual(s_line.index_id, index)

    def test_json_data(self):
        self._bind_products(self.prod, backend=self.backend)
        s_line = self._create_line(monday=False, tuesday=False)
        expected = {
            "config_id": s_line.seasonal_config_id.id,
            "date_end": "2021-05-16T02:00:00+02:00",
            "date_start": "2021-05-10T02:00:00+02:00",
            "id": s_line.id,
            "objectID": s_line.record_id.id,
            "product_ids": [s_line.product_id.id],
            "weekdays": [0, 3, 4, 5, 6],
        }
        self.assertEqual(s_line.get_shop_data(), expected)
        # change value
        s_line.monday = True
        expected["weekdays"] = [0, 1, 3, 4, 5, 6]
        self.assertEqual(s_line.get_shop_data(), expected)
