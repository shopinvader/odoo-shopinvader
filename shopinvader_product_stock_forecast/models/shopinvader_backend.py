# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    product_stock_forecast = fields.Boolean(
        string="Stock Forecast",
        help="Index the list of stock planned operations.",
    )
    product_stock_forecast_horizon = fields.Integer(
        string="Stock Forecast Horizon",
        help="Maximum number of days in the future to forecast.\n"
        "Set to 0 for unlimited forecasting.",
    )
    product_stock_field_name = fields.Char(
        related="product_stock_field_id.name",
        help="Technical field: Used only to display a warning on the view.",
    )
