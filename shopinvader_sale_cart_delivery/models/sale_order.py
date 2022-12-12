# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def _is_delivery_method_available(self, method_id):
        """
        Check if the mehtod is supported for the given SO
        """
        if self.env["delivery.carrier"].browse(method_id).exists():
            return method_id in self._get_available_carrier().ids
        return False
