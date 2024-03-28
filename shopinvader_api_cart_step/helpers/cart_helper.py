# Copyright 2024 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ShopinvaderApiCartRouterHelper(models.AbstractModel):
    _inherit = "shopinvader_api_cart.cart_router.helper"

    def _update_prepare_data(self, data):
        vals = super()._update_prepare_data(data)
        if data.current_step or data.next_step:
            vals.update(self._update_prepare_data_step(data))
        return vals

    def _update_prepare_data_step(self, data):
        return self.env["sale.order"]._cart_step_update_vals(
            current_step=data.current_step, next_step=data.next_step
        )
