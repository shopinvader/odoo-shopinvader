# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_api_cart.schemas.cart import (
    CartUpdateInput as BaseCartUpdateInput,
)


class CartUpdateInput(BaseCartUpdateInput, extends=True):
    warehouse_id: int | None = None

    def _to_sale_order_vals(self):
        vals = super()._to_sale_order_vals()
        if self.warehouse_id is not None:
            vals["warehouse_id"] = self.warehouse_id
        return vals
