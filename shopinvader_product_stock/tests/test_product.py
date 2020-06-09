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
        self._init_job_counter()
        self._add_stock_to_product(self.product, self.loc_1, 100)
        self._check_nbr_job_created(1)

    def test_update_stock_on_new_product(self):
        """
        Recomputing binding which have been not exported yet, do nothing
        """
        self.assertEqual(self.product.shopinvader_bind_ids.sync_state, "new")
        self.product._synchronize_all_binding_stock_level()
        self.assertEqual(self.product.shopinvader_bind_ids.data, {})

    def _test_update_stock_with_key(self, key_stock, sync_immediatly=True):
        shopinvader_product = self.product.shopinvader_bind_ids
        self._init_stock_to_zero(self.product, self.loc_1)
        self._init_stock_to_zero(self.product, self.loc_2)
        shopinvader_product.recompute_json()
        shopinvader_product.sync_state = "to_update"
        self.assertEqual(
            shopinvader_product.data[key_stock], {u"global": {u"qty": 0.0}}
        )

        self._init_job_counter()
        self._add_stock_to_product(self.product, self.loc_1, 100)
        self._check_nbr_job_created(1)

        with SeAdapterFake.mocked_calls() as calls:
            self._perform_created_job()

        self.assertEqual(
            shopinvader_product.data[key_stock], {u"global": {u"qty": 100.0}}
        )
        if sync_immediatly:
            self.assertEqual(len(calls), 1)
            call = calls[0]
            self.assertEqual(call["method"], "index")
            self.assertEqual(len(call["args"]), 1)
            self.assertEqual(
                call["args"][0][key_stock], {u"global": {u"qty": 100.0}}
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

        self._init_job_counter()
        self._init_stock_to_zero(self.product, self.loc_1)
        self._add_stock_to_product(self.product, self.loc_1, 100)
        self._check_nbr_job_created(1)
        self._perform_created_job()
        self.assertNotIn("stock", shopinvader_product.data)

    def test_multi_warehouse(self):
        wh_ids = [self.warehouse_1.id, self.warehouse_2.id]
        self.shopinvader_backend.write({"warehouse_ids": [(6, 0, wh_ids)]})
        self._init_stock_to_zero(self.product, self.loc_1)
        self._init_stock_to_zero(self.product, self.loc_2)
        shopinvader_product = self.product.shopinvader_bind_ids
        shopinvader_product.recompute_json()
        shopinvader_product.sync_state = "to_update"
        self.assertEqual(
            shopinvader_product.data["stock"],
            {
                u"wh2": {u"qty": 0.0},
                u"global": {u"qty": 0.0},
                u"wh": {u"qty": 0.0},
            },
        )

        self._init_job_counter()
        self._add_stock_to_product(self.product, self.loc_1, 100)
        self._add_stock_to_product(self.product, self.loc_2, 200)
        self._check_nbr_job_created(1)
        with SeAdapterFake.mocked_calls():
            self._perform_created_job()

        self.assertEqual(
            shopinvader_product.data["stock"],
            {
                u"wh2": {u"qty": 200.0},
                u"global": {u"qty": 300.0},
                u"wh": {u"qty": 100.0},
            },
        )
