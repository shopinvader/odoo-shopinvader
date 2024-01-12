# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def _action_confirm_cart_from_tx(self, tx):
        """
        Create a callback method that will be called when the related
        payment transaction will be confirmed.
        This method confirms the cart if transaction succeeded.
        """
        if tx.state == "done":
            return self.action_confirm_cart()
        return False
