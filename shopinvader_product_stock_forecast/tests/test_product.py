# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import tagged

from .common import StockForecastCommonCase


@tagged("post_install", "-at_install")
class TestProductStockForecast(StockForecastCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Prepare some stock.moves to forecast
        cls.moves_data = [
            ("2021-12-01 06:00:00", 10),
            ("2021-12-01 07:30:00", -5),
            ("2021-12-01 08:00:00", 10),
            ("2021-12-02 06:00:00", 20),
            ("2021-12-02 10:30:00", -5),
            ("2021-12-03 06:00:00", 20),
            ("2021-12-04 10:30:00", -5),
            ("2021-12-05 07:30:00", -10),
        ]
        cls._create_stock_moves(cls.moves_data)._action_confirm(merge=False)
        # Prepare other moves in draft and cancel states, just to create some noise
        cls._create_stock_moves([("2021-12-01 16:30:00", 9)])
        cls._create_stock_moves([("2021-12-01 16:30:00", 2)])._action_cancel()

    def test_stock_forecast_disabled(self):
        self.shopinvader_backend.product_stock_forecast = False
        self.shopinvader_product.invalidate_cache()
        self.shopinvader_product.recompute_json()
        self.assertNotIn("forecast", self.shopinvader_product.data["stock"]["global"])

    def test_stock_forecast_simple(self):
        self.shopinvader_product.invalidate_cache()
        self.shopinvader_product.recompute_json()
        forecast = self.shopinvader_product.data["stock"]["global"]["forecast"]
        self.assertEqual(self._to_moves_data(forecast), self.moves_data)

    def test_stock_forecast_horizon_1_days(self):
        self.shopinvader_backend.product_stock_forecast_horizon = 1  # days
        self.shopinvader_product.invalidate_cache()
        self.shopinvader_product.recompute_json()
        forecast = self.shopinvader_product.data["stock"]["global"]["forecast"]
        expected = [
            ("2021-12-01 06:00:00", 10),
            ("2021-12-01 07:30:00", -5),
            ("2021-12-01 08:00:00", 10),
        ]
        self.assertEqual(self._to_moves_data(forecast), expected)

    def test_stock_forecast_horizon_2_days(self):
        self.shopinvader_backend.product_stock_forecast_horizon = 2  # days
        self.shopinvader_product.invalidate_cache()
        self.shopinvader_product.recompute_json()
        forecast = self.shopinvader_product.data["stock"]["global"]["forecast"]
        expected = [
            ("2021-12-01 06:00:00", 10),
            ("2021-12-01 07:30:00", -5),
            ("2021-12-01 08:00:00", 10),
            ("2021-12-02 06:00:00", 20),
            ("2021-12-02 10:30:00", -5),
        ]
        self.assertEqual(self._to_moves_data(forecast), expected)

    def test_stock_forecast_order(self):
        """Forecast should always be sorted"""
        self._create_stock_moves([("2021-12-01 10:00:00", 10)])._action_confirm(
            merge=False
        )
        self.shopinvader_product.invalidate_cache()
        self.shopinvader_product.recompute_json()
        forecast = self.shopinvader_product.data["stock"]["global"]["forecast"]
        expected = [
            ("2021-12-01 06:00:00", 10),
            ("2021-12-01 07:30:00", -5),
            ("2021-12-01 08:00:00", 10),
            ("2021-12-01 10:00:00", 10),  # ⬅ new move
            ("2021-12-02 06:00:00", 20),
            ("2021-12-02 10:30:00", -5),
            ("2021-12-03 06:00:00", 20),
            ("2021-12-04 10:30:00", -5),
            ("2021-12-05 07:30:00", -10),
        ]
        self.assertEqual(self._to_moves_data(forecast), expected)
