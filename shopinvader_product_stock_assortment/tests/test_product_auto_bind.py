# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import SavepointCase


class TestProductAutoBind(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProductAutoBind, cls).setUpClass()
        cls.backend = cls.env.ref("shopinvader.backend_1")
        cls.variant_obj = cls.env["shopinvader.variant"]
        cls.product_obj = cls.env["product.product"]
        cls.product_qty_obj = cls.env["stock.change.product.qty"]
        cls.wh_obj = cls.env["stock.warehouse"]
        cls.product = cls.env.ref("product.product_product_9")
        cls.product.write({"sale_ok": True})
        cls.filter = cls.env.ref(
            "shopinvader_assortment.shopinvader_assortment1"
        )
        cls._create_warehouses()
        cls.backend.write({"warehouse_ids": [(6, False, cls.warehouses.ids)]})

    @classmethod
    def _create_warehouses(cls):
        cls.wh1 = cls.wh_obj.create({"name": "WH1", "code": "W1"})
        cls.wh2 = cls.wh_obj.create({"name": "WH2", "code": "W2"})
        cls.warehouses = cls.wh1 | cls.wh2

    def _update_product_quantity(
        self, quantity=20, product=False, location=False
    ):
        """
        Create a product and change the stock available.
        This function create a new product if it's not given.
        :param quantity: float
        :param product: product.product recordset or False
        :param location: stock.location recordset or False
        :return: product.product recordset
        """
        values = {"product_id": product.id, "new_quantity": quantity}
        if location:
            values.update({"location_id": location.id})
        wizard = self.product_qty_obj.create(values)
        wizard.change_product_qty()
        return product

    def test_shopinvader_auto_product_auto_bind(self):
        """
        For this test, ensure the binding use correctly the warehouse
        set on the shopinvader backend.
        Use case of this test:
        - For a product, set a quantity for a specific warehouse
        - For the same product, set a different quantity for another warehouse
        Then update the assortment domain to use the sum of these 2 warehouses.
        Finally launch the binding and the product should be in.
        :return:
        """
        # First step: ensure it's not binding with qty = 0
        location1 = self.wh1.lot_stock_id
        location2 = self.wh2.lot_stock_id
        self._update_product_quantity(0, self.product, location1)
        self._update_product_quantity(0, self.product, location2)
        # Ensure it's correct
        product = self.product.with_context(warehouse=self.warehouses.ids)
        product_obj = self.product_obj.with_context(
            warehouse=self.warehouses.ids
        )
        self.assertAlmostEqual(product.qty_available, 0)
        self.filter.write(
            {"domain": [("sale_ok", "=", True), ("qty_available", ">", 0)]}
        )
        # Test bind all products from assortment domain
        variants = self.variant_obj.search(
            [("backend_id", "=", self.backend.id)]
        )
        self.assertFalse(variants)
        domain = self.backend.product_assortment_id._get_eval_domain()
        products_to_bind = product_obj.search(domain)
        self.assertNotIn(self.product, products_to_bind)
        # Important to not use the env who contains warehouse ids.
        # It should be automatically into the binding.
        self.backend.autobind_product_from_assortment()
        variants = self.variant_obj.search(
            [("backend_id", "=", self.backend.id)]
        )
        self.assertNotIn(product, variants.mapped("record_id"))
        # Now use quantities > 0
        first_qty = 250
        second_qty = 100
        self._update_product_quantity(first_qty, self.product, location1)
        self._update_product_quantity(second_qty, self.product, location2)
        # Ensure it's correct
        total = first_qty + second_qty
        self.assertAlmostEqual(product.qty_available, total)
        self.filter.write(
            {"domain": [("sale_ok", "=", True), ("qty_available", "=", total)]}
        )
        self.backend.autobind_product_from_assortment()
        variants = self.variant_obj.search(
            [("backend_id", "=", self.backend.id)]
        )
        self.assertIn(product, variants.mapped("record_id"))
