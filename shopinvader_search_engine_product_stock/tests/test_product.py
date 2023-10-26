# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import StockCommonCase


class TestProductProduct(StockCommonCase):
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
            key = self.index._make_warehouse_key(wh)
            res[key] = {"qty": prod.with_context(warehouse=wh.id).qty_available}
        return res

    def test_update_qty_from_wizard(self):
        """Updating the quantity through an inventory create a job."""
        job = self.job_counter()
        self._add_stock_to_product(self.product, self.loc_1, 100)
        self.assertEqual(job.count_created(), 1)

    def _test_update_stock(self, sync_immediatly=True):
        self.product_binding.recompute_json()
        self.assertEqual(self.product_binding.data["stock"], {"global": {"qty": 0.0}})

        jobs = self.job_counter()
        self._add_stock_to_product(self.product, self.loc_1, 100)
        self.assertEqual(jobs.count_created(), 1)

        self.product.invalidate_recordset(["stock_data"])

        with self.se_adapter.mocked_calls() as calls:
            self.perform_jobs(jobs)

        self.assertEqual(self.product_binding.data["stock"], {"global": {"qty": 100.0}})
        if sync_immediatly:
            self.assertEqual(len(calls), 1)
            call = calls[0]
            self.assertEqual(call["method"], "index")
            self.assertEqual(len(call["args"]), 1)
            self.assertEqual(call["args"][0]["stock"], {"global": {"qty": 100.0}})
            self.assertEqual(self.product_binding.state, "done")
        else:
            self.assertEqual(len(calls), 0)
            self.assertEqual(self.product_binding.state, "to_export")

    def test_update_stock(self):
        """Recompute product should update binding and export it."""
        self._test_update_stock()

    def test_update_stock_differed(self):
        """Recompute product should update binding and not export it."""
        self.index.synchronize_stock = "in_batch"
        self._test_update_stock(sync_immediatly=False)

    def test_multi_warehouse(self):
        warehouses = self.warehouse_1 + self.warehouse_2
        self.index.write({"warehouse_ids": [(6, 0, warehouses.ids)]})

        self.product_binding.recompute_json()
        expected = self._expectect_qty_by_wh(warehouses, self.product)
        self.assertEqual(self.product_binding.data["stock"], expected)

        jobs = self.job_counter()
        self._add_stock_to_product(self.product, self.loc_1, 100)
        self._add_stock_to_product(self.product, self.loc_2, 200)

        self.product.invalidate_recordset(["stock_data"])
        self.assertEqual(jobs.count_created(), 1)
        with self.se_adapter.mocked_calls():
            self.perform_jobs(jobs)
        expected = self._expectect_qty_by_wh(warehouses, self.product)
        self.assertEqual(self.product_binding.data["stock"], expected)
