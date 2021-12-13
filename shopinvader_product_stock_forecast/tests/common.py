# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from freezegun import freeze_time

from odoo import fields

from odoo.addons.shopinvader_product_stock.tests.common import StockCommonCase


def isoformat2odoo(datestr):
    # replaces the fromisoformatm, not available in python 3.6
    # in python >= 3.7 it could be done like this:
    # return fields.Datetime.to_string(datetime.fromisoformat(datestr))
    format_string = r"%Y-%m-%dT%H:%M:%S"
    dt = datetime.strptime(datestr, format_string)
    return fields.Datetime.to_string(dt)


@freeze_time("2021-12-01 00:00:00")
class StockForecastCommonCase(StockCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Differently than on super(), here we want to disable jobs delay
        cls.env = cls.env(context=dict(cls.env.context, test_queue_job_no_delay=True))
        # Prepare some stock.moves to forecast
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.loc_customers = cls.env.ref("stock.stock_location_customers")
        # Make sure stock is always recomputed. If the state is "new", it"s ignored
        cls.shopinvader_product = cls.product.shopinvader_bind_ids
        cls.shopinvader_product.sync_state = "to_update"
        cls.shopinvader_product.recompute_json()
        # Enable Stock Forecast
        cls.shopinvader_backend.product_stock_forecast = True

    @classmethod
    def _create_stock_moves(cls, moves_data, location=None, product=None):
        if not location:
            location = cls.loc_1
        if not product:
            product = cls.product

        def prepare_out_vals():
            return {
                "picking_type_id": cls.picking_type_out.id,
                "location_id": location.id,
                "location_dest_id": cls.loc_customers.id,
            }

        def prepare_in_vals():
            return {
                "picking_type_id": cls.picking_type_in.id,
                "location_id": cls.loc_supplier.id,
                "location_dest_id": location.id,
            }

        def prepare_vals(data):
            date, qty = data
            vals = prepare_in_vals() if qty >= 0 else prepare_out_vals()
            vals.update(
                {
                    "name": "Forecasted stock.move",
                    "product_id": product.id,
                    "product_uom": cls.product.uom_id.id,
                    "product_uom_qty": abs(qty),
                    "date": date,
                }
            )
            return vals

        vals_list = list(map(prepare_vals, moves_data))
        return cls.env["stock.move"].create(vals_list)

    def _to_moves_data(self, forecast_data):
        return [(isoformat2odoo(d["date"]), d["qty"]) for d in forecast_data]
