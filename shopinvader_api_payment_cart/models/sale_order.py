# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def _action_confirm_cart_from_tx(self, tx):
        """
        Create a callback method that will be called when the related
        payment transaction will be confirmed.
        This method confirms the cart (into a quotation) if transaction succeeded.
        For custom payments, the transaction will never be done automatically
        but goes into "pending" state as soon as a wire transfer request was made
        (as in standard Odoo flow).
        What's more, if configured so on the payment provider, auto-confirm
        the quotation.
        """
        if tx.state == "done" or (
            tx.provider_id.code == "custom" and tx.state == "pending"
        ):
            res = self.action_confirm_cart()
            if tx.provider_id.shopinvader_auto_confirm_linked_so:
                self.action_confirm()
            return res
        return False
