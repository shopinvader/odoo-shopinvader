# Copyright 2021 Camptocamp SA (http://www.camptocamp.com).
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.tests.common import ComponentRegistryCase
from odoo.addons.product_seasonality.tests.common import CommonCaseWithLines
from odoo.addons.shopinvader_restapi.tests.common import UtilsMixin

# Reminders for lines' data (from CommonCaseWithLines):
#
# line_values = [
#     {
#         "date_start": "2021-05-10",
#         "date_end": "2021-05-16",
#         "monday": True,
#         "tuesday": True,
#         "wednesday": True,
#         "thursday": False,
#         "friday": False,
#         "saturday": False,
#         "sunday": False,
#         "product_template_id": cls.prod1.product_tmpl_id.id,
#         "product_id": cls.prod1.id,
#     },
#     {
#         "date_start": "2021-05-12",
#         "date_end": "2021-05-23",
#         "monday": False,
#         "tuesday": False,
#         "wednesday": False,
#         "thursday": True,
#         "friday": True,
#         "saturday": True,
#         "sunday": True,
#         "product_template_id": cls.prod2.product_tmpl_id.id,
#         "product_id": cls.prod2.id,
#     },
# ]


class TestProductSeasonalityCase(
    CommonCaseWithLines, UtilsMixin, ComponentRegistryCase
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, test_queue_job_no_delay=True))
        ComponentRegistryCase._setup_registry(cls)
        cls._load_module_components(cls, "shopinvader_product_seasonality")

        cls.line1 = cls.seasonal_conf.config_for_product(cls.prod1)
        cls.line2 = cls.seasonal_conf.config_for_product(cls.prod2)
        cls.config_line_model = cls.env["seasonal.config.line"]
        cls.s_config_line_model = cls.env["shopinvader.seasonal.config.line"]
        cls.backend = cls.env.ref("shopinvader_restapi.backend_1")
        cls.s_line1 = cls.s_config_line_model.create(
            {
                "record_id": cls.line1.id,
                "backend_id": cls.backend.id,
            }
        )
        cls.s_line2 = cls.s_config_line_model.create(
            {
                "record_id": cls.line2.id,
                "backend_id": cls.backend.id,
            }
        )

    def test_weekdays(self):
        self.assertEqual(self.s_line1.weekdays, [1, 2, 3])
        self.assertEqual(self.s_line2.weekdays, [0, 4, 5, 6])
        self.line1.with_context(foo=1).write(
            {
                "monday": False,
                "saturday": True,
            }
        )
        self.assertEqual(self.s_line1.weekdays, [2, 3, 6])

    def test_shop_data(self):
        # NOTE: if this test fails locally when running tests for the 2nd time
        # check if you have installed `*_search_engine` integration
        # because data won't be computed.
        # Just uninstall the module and run tests again.
        data = self.s_line1.get_shop_data()
        expected = {
            "objectID": self.line1.id,
            "config_id": self.line1.seasonal_config_id.id,
            "product_ids": list(self.line1.product_template_id.product_variant_ids.ids),
            "date_start": "2021-05-10T02:00:00+02:00",
            "date_end": "2021-05-16T02:00:00+02:00",
            "weekdays": [1, 2, 3],
        }
        for k, v in expected.items():
            self.assertEqual(data[k], v, f"`{k}` does not match `f{v}`")

        data = self.s_line2.get_shop_data()
        expected = {
            "objectID": self.line2.id,
            "config_id": self.line2.seasonal_config_id.id,
            "product_ids": list(self.line2.product_template_id.product_variant_ids.ids),
            "date_start": "2021-05-12T02:00:00+02:00",
            "date_end": "2021-05-23T02:00:00+02:00",
            "weekdays": [0, 4, 5, 6],
        }
        for k, v in expected.items():
            self.assertEqual(data[k], v, f"`{k}` does not match `f{v}`")

    def test_auto_create_binding(self):
        self._bind_products(self.prod2, backend=self.backend)
        line = self.config_line_model.create(
            {
                "date_start": "2021-05-12",
                "date_end": "2021-05-23",
                "saturday": False,
                "sunday": False,
                "product_template_id": self.prod2.product_tmpl_id.id,
                "product_id": self.prod2.id,
                "seasonal_config_id": self.line2.seasonal_config_id.id,
            }
        )
        self.assertEqual(len(line.shopinvader_bind_ids), 1)
        self.assertEqual(line.shopinvader_bind_ids[0].product_ids, [self.prod2.id])

    def test_auto_create_binding_from_template(self):
        self._bind_products(self.prod2, backend=self.backend)
        line = self.config_line_model.create(
            {
                "date_start": "2021-05-12",
                "date_end": "2021-05-23",
                "saturday": False,
                "sunday": False,
                "product_template_id": self.prod2.product_tmpl_id.id,
                "seasonal_config_id": self.line2.seasonal_config_id.id,
            }
        )
        all_variants = self.prod2.product_tmpl_id.product_variant_ids
        # We must have 1 binding per each variant
        self.assertTrue(len(all_variants) > 1)
        self.assertEqual(len(line.shopinvader_bind_ids), 1)
        self.assertEqual(
            sorted(line.shopinvader_bind_ids[0].product_ids),
            sorted(all_variants.ids),
        )

    def test_auto_update_binding(self):
        # expected = {
        #     "objectID": self.line2.id,
        #     "config_id": self.line2.seasonal_config_id.id,
        #     "product_ids": list(self.line2.product_template_id.product_variant_ids.ids),
        #     "date_start": "2021-05-12T02:00:00+02:00",
        #     "date_end": "2021-05-23T02:00:00+02:00",
        #     "weekdays": [0, 4, 5, 6],
        # }
        data = self.s_line2.get_shop_data()
        self.assertEqual(data["weekdays"], [0, 4, 5, 6])

    def test_bind_all_existing(self):
        line = self.config_line_model.create(
            {
                "date_start": "2021-05-12",
                "date_end": "2021-05-23",
                "saturday": False,
                "sunday": False,
                "product_template_id": self.prod2.product_tmpl_id.id,
                "product_id": self.prod2.id,
                "seasonal_config_id": self.line2.seasonal_config_id.id,
            }
        )
        # no bound product, no binding
        self.assertEqual(len(line.shopinvader_bind_ids), 0)
        self.backend.bind_all_seasonal_config_lines()
        self.assertEqual(len(line.shopinvader_bind_ids), 0)
        self._bind_products(self.prod2, backend=self.backend)
        self.backend.bind_all_seasonal_config_lines()
        self.assertEqual(len(line.shopinvader_bind_ids), 1)
