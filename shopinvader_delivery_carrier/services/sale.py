# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class SaleService(Component):
    _inherit = "shopinvader.sale.service"
    _usage = "sales"

    def _convert_one_sale(self, sale):
        res = super()._convert_one_sale(sale)
        res["deliveries"] = self._convert_deliveries(sale)
        return res

    def _convert_deliveries(self, sale):
        res = []
        for picking in sale.sudo().picking_ids.filtered(
            lambda l: l.state in ["assigned", "done"]
        ):
            res.append(self._convert_one_delivery(picking))
        return res

    def _convert_one_delivery(self, delivery):
        return {
            "id": delivery.id,
            "name": delivery.name,
            "date": delivery.date_done or delivery.scheduled_date or None,
        }
