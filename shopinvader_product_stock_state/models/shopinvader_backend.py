# Copyright 2018 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    stock_level_config = fields.Selection(
        selection=[
            ("state_and_low_qty", "State and Low Quantity"),
            ("state_and_qty", "State and Quantity"),
            ("only_state", "Only State"),
            ("only_qty", "Only Quantity"),
        ],
        default="state_and_low_qty",
        required=True,
    )
