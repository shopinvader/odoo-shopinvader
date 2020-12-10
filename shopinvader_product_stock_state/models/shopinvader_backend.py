# Copyright 2018 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    def _selection_stock_level_config(self):
        return super()._selection_stock_level_config() + [
            ("state_and_low_qty", "State and Low Quantity"),
            ("state_and_qty", "State and Quantity"),
            ("only_state", "Only State"),
        ]
