# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from psycopg2 import sql

from odoo import fields, models


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    def _prepare_stock_forecast_select(self):
        return """
            m.date AS date,
            SUM(
                CASE
                WHEN whs.id IS NOT NULL AND whd.id IS NULL THEN -m.product_qty
                WHEN whd.id IS NOT NULL AND whs.id IS NULL THEN m.product_qty
                END
            ) AS qty
        """

    def _prepare_stock_forecast_from(self):
        return """
            stock_move m
            LEFT JOIN stock_location ls ON (ls.id=m.location_id)
            LEFT JOIN stock_location ld ON (ld.id=m.location_dest_id)
            LEFT JOIN stock_warehouse whs
                ON ls.parent_path LIKE CONCAT('%%/', whs.view_location_id, '/%%')
            LEFT JOIN stock_warehouse whd
                ON ld.parent_path LIKE CONCAT('%%/', whd.view_location_id, '/%%')
        """

    def _prepare_stock_forecast_where_clause(self):
        """Prepare the where and where params for the forecast query"""
        where_clause = """
            m.product_id = %s
            AND m.state NOT IN ('cancel', 'draft', 'done')
            AND (whs.id IS NOT NULL OR whd.id IS NOT NULL)
            AND (whs.id IS NULL OR whd.id IS NULL OR whs.id != whd.id)
        """
        where_clause_params = [self.record_id.id]
        # Warehouse
        warehouse_ids = self.env.context.get("warehouse", [])
        if warehouse_ids:
            where_clause += """
                AND (
                    CASE
                    WHEN whs.id IS NOT NULL AND whd.id IS NULL THEN whs.id
                    WHEN whd.id IS NOT NULL AND whs.id IS NULL THEN whd.id
                    END
                ) IN %s
            """
            where_clause_params.append(tuple(warehouse_ids))
        # Forecast Horizon
        if self.backend_id.product_stock_forecast_horizon:
            horizon = self.backend_id.product_stock_forecast_horizon
            dt_end = fields.Datetime.now() + timedelta(days=horizon)
            where_clause += "\nAND m.date <= %s"
            where_clause_params.append(dt_end)
        return where_clause, where_clause_params

    def _prepare_stock_forecast_group_by(self):
        return "m.date"

    def _prepare_stock_forecast_order_by(self):
        return "1 ASC"

    def _prepare_stock_forecast_raw_data(self):
        """Prepare the stock forecast raw data

        :returns: list of dicts {date, qty}
            date: date of the forecast move
            qty: stock variation
        """
        query = sql.SQL(
            """
            SELECT {select}
            FROM {from_clause}
            WHERE {where_clause}
            GROUP BY {group_by}
            ORDER BY {order_by}
            """
        )
        where_clause, params = self._prepare_stock_forecast_where_clause()
        query = query.format(
            select=sql.SQL(self._prepare_stock_forecast_select()),
            from_clause=sql.SQL(self._prepare_stock_forecast_from()),
            where_clause=sql.SQL(where_clause),
            group_by=sql.SQL(self._prepare_stock_forecast_group_by()),
            order_by=sql.SQL(self._prepare_stock_forecast_order_by()),
        )
        self.env["base"].flush()
        self.env.cr.execute(query, params)
        return self.env.cr.dictfetchall()

    def _prepare_stock_forecast_data(self):
        """Prepare the stock forecast data, ready to be serialized"""
        data = self._prepare_stock_forecast_raw_data()
        # Convert date to string, for it to be serializable
        # TODO: Possibly use this encoder everywhere in shopinvader
        # https://github.com/OCA/rest-framework/blob/e9bb95272/base_rest/http.py#L47
        for row in data:
            row["date"] = row["date"].isoformat()
        return data

    def _prepare_stock_data(self):
        # OVERRIDE to add the stock forecast data
        res = super()._prepare_stock_data()
        if self.backend_id.product_stock_forecast:
            res["forecast"] = self._prepare_stock_forecast_data()
        return res
