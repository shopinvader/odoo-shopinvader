# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.connector_search_engine.tests.models import SeAdapterFake

from .common import StockCommonCase


class TestProductProduct(StockCommonCase):
    """
    Tests for product.product
    """

    def test_update_qty_from_wizard(self):
        """
        Test that updating the quantity through an inventory create a
        new queue.job
        """
        job = self.job_counter()
        self._add_stock_to_product(self.product, self.loc_1, 100)
        self.assertEqual(job.count_created(), 1)

    def test_update_stock_on_new_product(self):
        """
        Recomputing binding which have been not exported yet, do nothing
        """
        self.assertEqual(self.product.shopinvader_bind_ids.sync_state, "new")
        self.product._synchronize_all_binding_stock_level()
        self.assertEqual(self.product.shopinvader_bind_ids.data, {})

    def _test_update_stock_with_key(self, key_stock, sync_immediatly=True):
        shopinvader_product = self.product.shopinvader_bind_ids
        shopinvader_product.recompute_json()
        shopinvader_product.sync_state = "to_update"
        self.assertEqual(
            shopinvader_product.data[key_stock], {"global": {"qty": 0.0}}
        )

        jobs = self.job_counter()
        self._add_stock_to_product(self.product, self.loc_1, 100)
        self.assertEqual(jobs.count_created(), 1)

        with SeAdapterFake.mocked_calls() as calls:
            self.perform_jobs(jobs)

        self.assertEqual(
            shopinvader_product.data[key_stock], {"global": {"qty": 100.0}}
        )
        if sync_immediatly:
            self.assertEqual(len(calls), 1)
            call = calls[0]
            self.assertEqual(call["method"], "index")
            self.assertEqual(len(call["args"]), 1)
            self.assertEqual(
                call["args"][0][key_stock], {"global": {"qty": 100.0}}
            )
            self.assertEqual(shopinvader_product.sync_state, "done")
        else:
            self.assertEqual(len(calls), 0)
            self.assertEqual(shopinvader_product.sync_state, "to_update")

    def test_update_stock(self):
        """
        Recomputing product should update binding and export it
        """
        self._test_update_stock_with_key("stock")

    def test_update_stock_differed(self):
        """
        Recomputing product should update binding and not export it
        """
        self.shopinvader_backend.synchronize_stock = "in_batch"
        self._test_update_stock_with_key("stock", sync_immediatly=False)

    def test_update_stock_with_special_key(self):
        """
        Recomputing product should update binding
        using the custom key defined by the user
        """
        export_line = self.env.ref(
            "shopinvader_product_stock."
            "ir_exp_shopinvader_variant_stock_data"
        )
        export_line.alias = "stock_data:custom_stock"
        self._test_update_stock_with_key("custom_stock")

    def test_update_stock_without_alias(self):
        """
        Recomputing product should update binding
        Using the name as key
        """
        export_line = self.env.ref(
            "shopinvader_product_stock."
            "ir_exp_shopinvader_variant_stock_data"
        )
        export_line.alias = None
        self._test_update_stock_with_key("stock_data")

    def test_update_stock_without_key(self):
        """
        Recomputing product should update binding
        Without export line
        """
        export_line = self.env.ref(
            "shopinvader_product_stock."
            "ir_exp_shopinvader_variant_stock_data"
        )
        export_line.unlink()

        shopinvader_product = self.product.shopinvader_bind_ids
        shopinvader_product.recompute_json()
        shopinvader_product.sync_state = "to_update"
        self.assertNotIn("stock", shopinvader_product.data)

        jobs = self.job_counter()
        self._add_stock_to_product(self.product, self.loc_1, 100)
        self.assertEqual(jobs.count_created(), 1)
        self.perform_jobs(jobs)
        self.assertNotIn("stock", shopinvader_product.data)

    def test_multi_warehouse(self):
        wh_ids = [self.warehouse_1.id, self.warehouse_2.id]
        self.shopinvader_backend.write({"warehouse_ids": [(6, 0, wh_ids)]})
        shopinvader_product = self.product.shopinvader_bind_ids
        shopinvader_product.recompute_json()
        shopinvader_product.sync_state = "to_update"
        self.assertEqual(
            shopinvader_product.data["stock"],
            {
                "chic": {"qty": 0.0},
                "global": {"qty": 0.0},
                "wh": {"qty": 0.0},
            },
        )

        jobs = self.job_counter()
        self._add_stock_to_product(self.product, self.loc_1, 100)
        self._add_stock_to_product(self.product, self.loc_2, 200)
        self.assertEqual(jobs.count_created(), 1)
        with SeAdapterFake.mocked_calls():
            self.perform_jobs(jobs)

        self.assertEqual(
            shopinvader_product.data["stock"],
            {
                "chic": {"qty": 200.0},
                "global": {"qty": 300.0},
                "wh": {"qty": 100.0},
            },
        )
