# Copyright 2021 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class SaleService(Component):
    _inherit = "shopinvader.sale.service"

    def _convert_one_move(self, move):
        variant = move.product_id._get_invader_variant(
            self.shopinvader_backend, self.env.context.get("lang")
        )
        product = self._convert_one_line_product(variant)
        return {
            "quantity": move.product_qty,
            "product": product,
        }

    def _convert_moves(self, delivery):
        items = []
        for move in delivery.move_lines:
            items.append(self._convert_one_move(move))
        return items

    def _convert_one_delivery(self, delivery):
        res = super()._convert_one_delivery(delivery)
        res["lines"] = self._convert_moves(delivery)
        res["state"] = delivery.state
        return res
