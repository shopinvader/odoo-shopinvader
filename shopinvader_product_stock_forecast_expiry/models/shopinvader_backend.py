# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    product_stock_forecast_expiry = fields.Selection(
        [
            ("no", "Ignore stock expiration"),
            ("expiration_date", "Expiration date"),
            ("use_date", "Best before date"),
            ("removal_date", "Removal date"),
        ],
        string="Stock Forecast Expiry",
        help="Accounts for stock expiration dates:\n\n"
        "* Ignore stock expiry: Disabled.\n"
        "* Expiration date: Stock is removed on lot expiration date.\n"
        "* Best before date: Stock is removed on lot best before date.\n"
        "* Removal date: Stock is removed on lot removal date.\n\n"
        "For incoming stocks, where the lot hasn't been created yet, the expiry dates "
        "will be computed from the product expiry settings.",
        default="removal_date",
        required=True,
    )
