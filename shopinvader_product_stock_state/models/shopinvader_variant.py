# Copyright 2018 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    def _prepare_stock_data(self):
        res = super(ShopinvaderVariant, self)._prepare_stock_data()
        config = self.backend_id.stock_level_config
        if "state" in config:
            res["state"] = self.stock_state
        if config == "only_state" or (
            config == "state_and_low_qty" and res["state"] == "in_stock"
        ):
            res.pop("qty")
        return res
