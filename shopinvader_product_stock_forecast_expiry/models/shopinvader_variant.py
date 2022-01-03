# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta
from itertools import chain

from odoo import models


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    def _prepare_stock_forecast_quants_expiry_data(self):
        """Returns the stock expirations for existing quants."""
        expiry_fname = self.backend_id.product_stock_forecast_expiry
        if not self.use_expiration_date or expiry_fname == "no":
            return []
        warehouse_ids = self.env.context.get("warehouse", [])
        warehouses = self.env["stock.warehouse"].browse(warehouse_ids)
        quants = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.record_id.id),
                ("location_id", "child_of", warehouses.lot_stock_id.ids),
                (f"lot_id.{expiry_fname}", "!=", False),
            ]
        )
        return [
            {"date": quant.lot_id[expiry_fname], "qty": -quant.quantity}
            for quant in quants
        ]

    def _prepare_stock_forecast_incoming_move_expiry_timedelta(self):
        """Returns the delta for the forecasted expiration date of incoming moves.

        This should match the computation done by core's `product_expiry` module in
        :meth:`~odoo.addons.product.models.production_lot._get_dates`.

        :returns: False if no expiry time is configured, otherwise a timedelta
        """
        expiry_fname = self.backend_id.product_stock_forecast_expiry
        mapped_fields = {
            "expiration_date": "expiration_time",
            "use_date": "use_time",
            "removal_date": "removal_time",
        }
        if (
            not self.use_expiration_date
            or expiry_fname not in mapped_fields
            or not self[mapped_fields[expiry_fname]]
        ):
            return False
        return timedelta(days=self[mapped_fields[expiry_fname]])

    def _prepare_stock_forecast_incoming_expiry_data(self, raw_data):
        """Returns the stock expirations for incoming moves.
        :param list data: As returned by super()._prepare_stock_forecast_data
        """
        tdelta = self._prepare_stock_forecast_incoming_move_expiry_timedelta()
        if not tdelta:
            return []
        # Future stock expiration dates for incoming moves
        return [
            {"date": d["date"] + tdelta, "qty": -d["qty"]}
            for d in raw_data
            if d["qty"] > 0
        ]

    def _prepare_stock_forecast_raw_data(self):
        # OVERRIDE to account for stock expiry. There are two sources:
        # 1. Expiration dates for the current stock lots.
        #    We simply get the list from the lots and add the corresponding lines.
        # 2. Future expiration dates for the incoming moves.
        #    For each incoming move, we compute the expiration date based on the
        #    product.product configuration.
        res = super()._prepare_stock_forecast_raw_data()
        expiry_fname = self.backend_id.product_stock_forecast_expiry
        if not self.use_expiration_date or expiry_fname == "no":
            return res
        # Add our expiry forecast
        quants_expiry_data = self._prepare_stock_forecast_quants_expiry_data()
        incoming_expiry_data = self._prepare_stock_forecast_incoming_expiry_data(res)
        return list(
            sorted(
                chain(res, quants_expiry_data, incoming_expiry_data),
                key=lambda r: r["date"],
            )
        )
