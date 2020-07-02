# Copyright 2018 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader_product_stock.tests.common import StockCommonCase


class TestProductProduct(StockCommonCase):
    """Tests for product stock info."""

    @classmethod
    def setUpClass(cls):
        super(TestProductProduct, cls).setUpClass()
        cls.shopinvader_product = cls.product.shopinvader_bind_ids
        cls.company = cls.env.ref("base.main_company")

    def test_out_of_stock(self):
        self.assertEqual(
            self.shopinvader_product.stock_data, {"global": {"state": "out_of_stock"}}
        )

    def test_in_limited_stock(self):
        self._add_stock_to_product(self.product, self.loc_1, 5)
        self.assertEqual(
            self.shopinvader_product.stock_data,
            {"global": {"state": "in_limited_stock", "qty": 5.0}},
        )

    def test_in_stock(self):
        self.company.stock_state_threshold = 0
        self._add_stock_to_product(self.product, self.loc_1, 20)
        self.assertEqual(
            self.shopinvader_product.stock_data, {"global": {"state": "in_stock"}}
        )

    def test_resupplying(self):
        move = self._create_incoming_move()
        move._action_confirm()
        self.assertEqual(
            self.shopinvader_product.stock_data, {"global": {"state": "resupplying"}}
        )

    def test_config_only_qty(self):
        self.shopinvader_backend.stock_level_config = "only_qty"
        self.assertEqual(
            self.shopinvader_product.stock_data, {"global": {"qty": 0.00}}
        )

    def test_config_only_state(self):
        self.shopinvader_backend.stock_level_config = "only_state"
        self._add_stock_to_product(self.product, self.loc_1, 5)
        self.assertEqual(
            self.shopinvader_product.stock_data,
            {"global": {"state": "in_limited_stock"}},
        )

    def test_config_state_and_qty(self):
        self.shopinvader_backend.stock_level_config = "state_and_qty"
        self.assertEqual(
            self.shopinvader_product.stock_data,
            {"global": {"qty": 0.00, "state": "out_of_stock"}},
        )
