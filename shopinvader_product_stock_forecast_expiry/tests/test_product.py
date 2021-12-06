# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo.tests.common import tagged

from odoo.addons.shopinvader_product_stock_forecast.tests.common import (
    StockForecastCommonCase,
)


@tagged("post_install", "-at_install")
class TestProductStockForecastExpiry(StockForecastCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Configure product expiration
        cls.product.tracking = "lot"
        cls.product.use_expiration_date = True
        cls.product.use_time = 1
        cls.product.expiration_time = 2
        cls.product.removal_time = 3
        # Prepare some initial stock, use freeze_time to have odoo compute
        # the proper expiration dates
        with freeze_time("2021-11-30 10:00:00"):
            cls._create_quant_and_lot(quantity=10)
        with freeze_time("2021-12-01 00:00:00"):
            cls._create_quant_and_lot(quantity=20)
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

    @classmethod
    def _create_quant_and_lot(cls, quantity=1.0, product=None, location=None):
        """Create a quant and a lot, and link them together"""
        location = location or cls.loc_1
        product = product or cls.product
        lot_vals = {
            "product_id": product.id,
            "company_id": location.company_id.id,
        }
        lot = cls.env["stock.production.lot"].create(lot_vals)
        quant_vals = {
            "product_id": product.id,
            "location_id": location.id,
            "quantity": quantity,
            "lot_id": lot.id,
        }
        return cls.env["stock.quant"].create(quant_vals)

    def test_stock_forecast_expiry_disabled(self):
        self.shopinvader_backend.product_stock_forecast_expiry = "no"
        self.shopinvader_product.invalidate_cache()
        self.shopinvader_product.recompute_json()
        forecast = self.shopinvader_product.data["stock"]["global"]["forecast"]
        self.assertEqual(self._to_moves_data(forecast), self.moves_data)

    def test_stock_forecast_expiry_disabled_on_product(self):
        self.product.use_expiration_date = False
        self.shopinvader_product.invalidate_cache()
        self.shopinvader_product.recompute_json()
        forecast = self.shopinvader_product.data["stock"]["global"]["forecast"]
        self.assertEqual(self._to_moves_data(forecast), self.moves_data)

    def test_stock_forecast_expiry_removal_date(self):
        self.shopinvader_backend.product_stock_forecast_expiry = "removal_date"
        self.shopinvader_product.invalidate_cache()
        self.shopinvader_product.recompute_json()
        forecast = self.shopinvader_product.data["stock"]["global"]["forecast"]
        expected = [
            ("2021-12-01 06:00:00", 10),
            ("2021-12-01 07:30:00", -5),
            ("2021-12-01 08:00:00", 10),
            ("2021-12-02 06:00:00", 20),
            ("2021-12-02 10:30:00", -5),
            ("2021-12-03 06:00:00", 20),
            ("2021-12-03 10:00:00", -10),  # from existing quants
            ("2021-12-04 00:00:00", -20),  # from existing quants
            ("2021-12-04 06:00:00", -10),  # from 1st incoming move
            ("2021-12-04 08:00:00", -10),  # from 2nd incoming move
            ("2021-12-04 10:30:00", -5),
            ("2021-12-05 06:00:00", -20),  # from 3rd incoming move
            ("2021-12-05 07:30:00", -10),
            ("2021-12-06 06:00:00", -20),  # from 4th incoming move
        ]
        self.assertEqual(self._to_moves_data(forecast), expected)

    def test_stock_forecast_expiry_expiration_date(self):
        self.shopinvader_backend.product_stock_forecast_expiry = "expiration_date"
        self.shopinvader_product.invalidate_cache()
        self.shopinvader_product.recompute_json()
        forecast = self.shopinvader_product.data["stock"]["global"]["forecast"]
        expected = [
            ("2021-12-01 06:00:00", 10),
            ("2021-12-01 07:30:00", -5),
            ("2021-12-01 08:00:00", 10),
            ("2021-12-02 06:00:00", 20),
            ("2021-12-02 10:00:00", -10),  # from existing quants
            ("2021-12-02 10:30:00", -5),
            ("2021-12-03 00:00:00", -20),  # from existing quants
            ("2021-12-03 06:00:00", 20),
            ("2021-12-03 06:00:00", -10),  # from 1st incoming move
            ("2021-12-03 08:00:00", -10),  # from 2nd incoming move
            ("2021-12-04 06:00:00", -20),  # from 3rd incoming move
            ("2021-12-04 10:30:00", -5),
            ("2021-12-05 06:00:00", -20),  # from 4th incoming move
            ("2021-12-05 07:30:00", -10),
        ]
        self.assertEqual(self._to_moves_data(forecast), expected)

    def test_stock_forecast_expiry_use_date(self):
        self.shopinvader_backend.product_stock_forecast_expiry = "use_date"
        self.shopinvader_product.invalidate_cache()
        self.shopinvader_product.recompute_json()
        forecast = self.shopinvader_product.data["stock"]["global"]["forecast"]
        expected = [
            ("2021-12-01 06:00:00", 10),
            ("2021-12-01 07:30:00", -5),
            ("2021-12-01 08:00:00", 10),
            ("2021-12-01 10:00:00", -10),  # from existing quants
            ("2021-12-02 00:00:00", -20),  # from existing quants
            ("2021-12-02 06:00:00", 20),
            ("2021-12-02 06:00:00", -10),  # from 1st incoming move
            ("2021-12-02 08:00:00", -10),  # from 2nd incoming move
            ("2021-12-02 10:30:00", -5),
            ("2021-12-03 06:00:00", 20),
            ("2021-12-03 06:00:00", -20),  # from 3rd incoming move
            ("2021-12-04 06:00:00", -20),  # from 4th incoming move
            ("2021-12-04 10:30:00", -5),
            ("2021-12-05 07:30:00", -10),
        ]
        self.assertEqual(self._to_moves_data(forecast), expected)
