# Copyright 2018 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    def _prepare_stock_data(self):
        res = super(ShopinvaderVariant, self)._prepare_stock_data()
        if "state" in self.backend_id.stock_level_config:
            res["state"] = self.stock_state
        if self._skip_stock_qty_update():
            res.pop("qty", None)
        return res

    def _skip_stock_qty_update(self):
        config = self.backend_id.stock_level_config
        return config == "only_state" or (
            config == "state_and_low_qty"
            and self.stock_state != "in_limited_stock"
        )
