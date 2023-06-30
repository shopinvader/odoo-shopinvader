# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.shopinvader.tests.common import UtilsMixin

from .common import StockCommonCase


class TestProductProduct(StockCommonCase, UtilsMixin):
    """Tests for product stock info."""

    def _expectect_qty_by_wh(self, warehouse_recs, prod):
        res = {
            "global": {
                "qty": prod.with_context(
                    warehouse=list(warehouse_recs.ids)
                ).qty_available
            },
        }
        for wh in warehouse_recs:
            key = self.shopinvader_backend._make_warehouse_key(wh)
            res[key] = {"qty": prod.with_context(warehouse=wh.id).qty_available}
        return res

    def test_update_qty_from_wizard(self):
        """Updating the quantity through an inventory create a job."""
        job = self.job_counter()
        self._add_stock_to_product(self.product, self.loc_1, 100)
        self.assertEqual(job.count_created(), 1)

    def test_update_stock_on_new_product(self):
        """Recompute binding not exported yet does nothing."""
        self.assertEqual(self.product.shopinvader_bind_ids.sync_state, "new")
        self.product.synchronize_all_binding_stock_level()
        self.assertEqual(self.product.shopinvader_bind_ids.data, {})

    def _test_update_stock_with_key(self, key_stock, sync_immediatly=True):
        shopinvader_product = self.product.shopinvader_bind_ids
        self._refresh_json_data(shopinvader_product, backend=self.shopinvader_backend)
        shopinvader_product.sync_state = "to_update"
        self.assertEqual(shopinvader_product.data[key_stock], {"global": {"qty": 0.0}})

        jobs = self.job_counter()
        self._add_stock_to_product(self.product, self.loc_1, 100)
        self.assertEqual(jobs.count_created(), 1)

        shopinvader_product.invalidate_cache(["stock_data"])

        with self.se_adapter_fake.mocked_calls() as calls:
            self.perform_jobs(jobs)

        self.assertEqual(
            shopinvader_product.data[key_stock], {"global": {"qty": 100.0}}
        )
        if sync_immediatly:
            self.assertEqual(len(calls), 1)
            call = calls[0]
            self.assertEqual(call["method"], "index")
            self.assertEqual(len(call["args"]), 1)
            self.assertEqual(call["args"][0][key_stock], {"global": {"qty": 100.0}})
            self.assertEqual(shopinvader_product.sync_state, "done")
        else:
            self.assertEqual(len(calls), 0)
            self.assertEqual(shopinvader_product.sync_state, "to_update")

    def test_update_stock(self):
        """Recompute product should update binding and export it."""
        self._test_update_stock_with_key("stock")

    def test_update_stock_differed(self):
        """Recompute product should update binding and not export it."""
        self.shopinvader_backend.synchronize_stock = "in_batch"
        self._test_update_stock_with_key("stock", sync_immediatly=False)

    def test_update_stock_with_special_key(self):
        """Recompute product should update binding using custom key by user."""
        export_line = self.env.ref(
            "shopinvader_product_stock." "ir_exp_shopinvader_variant_stock_data"
        )
        export_line.target = "stock_data:custom_stock"
        self._test_update_stock_with_key("custom_stock")

    def test_update_stock_without_target(self):
        """Recompute product should update binding using the name as key."""
        export_line = self.env.ref(
            "shopinvader_product_stock." "ir_exp_shopinvader_variant_stock_data"
        )
        export_line.target = None
        self._test_update_stock_with_key("stock_data")

    def test_update_stock_without_key(self):
        """Recompute product should update binding without export line."""
        export_line = self.env.ref(
            "shopinvader_product_stock." "ir_exp_shopinvader_variant_stock_data"
        )
        export_line.unlink()

        shopinvader_product = self.product.shopinvader_bind_ids
        self._refresh_json_data(shopinvader_product, backend=self.shopinvader_backend)
        shopinvader_product.sync_state = "to_update"
        self.assertNotIn("stock", shopinvader_product.data)

        jobs = self.job_counter()
        self._add_stock_to_product(self.product, self.loc_1, 100)
        self.assertEqual(jobs.count_created(), 1)
        self.perform_jobs(jobs)
        self.assertNotIn("stock", shopinvader_product.data)

    def test_multi_warehouse(self):
        warehouses = self.warehouse_1 + self.warehouse_2
        self.shopinvader_backend.write({"warehouse_ids": [(6, 0, warehouses.ids)]})

        shopinvader_product = self.product.shopinvader_bind_ids
        self._refresh_json_data(shopinvader_product, backend=self.shopinvader_backend)
        shopinvader_product.sync_state = "to_update"
        expected = self._expectect_qty_by_wh(warehouses, self.product)
        self.assertEqual(shopinvader_product.data["stock"], expected)

        jobs = self.job_counter()
        self._add_stock_to_product(self.product, self.loc_1, 100)
        self._add_stock_to_product(self.product, self.loc_2, 200)

        shopinvader_product.invalidate_cache(["stock_data"])
        self.assertEqual(jobs.count_created(), 1)
        with self.se_adapter_fake.mocked_calls():
            self.perform_jobs(jobs)
        expected = self._expectect_qty_by_wh(warehouses, self.product)
        self.assertEqual(shopinvader_product.data["stock"], expected)
