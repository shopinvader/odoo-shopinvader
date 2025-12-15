# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models
from odoo.osv import expression


class ShopinvaderApiWarehouseRouterHelper(models.AbstractModel):
    _inherit = "shopinvader_api_warehouse.warehouse_router.helper"

    def _get_sale_channel_id(self) -> int:
        return self.env.context.get("sale_channel_id")

    def _get_domain_adapter(self):
        return expression.AND(
            [
                super()._get_domain_adapter(),
                [("sale_channel_ids", "in", (self._get_sale_channel_id(),))],
            ]
        )
