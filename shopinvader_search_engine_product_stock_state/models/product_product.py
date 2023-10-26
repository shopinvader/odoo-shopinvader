# Copyright 2018 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _prepare_stock_data(self):
        self.ensure_one()
        res = super()._prepare_stock_data()
        index_id = self.env.context.get("index_id", False)
        if index_id:
            index = self.env["se.index"].browse(index_id)
            if "state" in index.stock_level_config:
                res["state"] = self.stock_state
            if self._skip_stock_qty_update(index):
                res.pop("qty", None)
        return res

    def _skip_stock_qty_update(self, index=None):
        self.ensure_one()
        if index:
            config = index.stock_level_config
            return config == "only_state" or (
                config == "state_and_low_qty" and self.stock_state != "in_limited_stock"
            )
        return False
