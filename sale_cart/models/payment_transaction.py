# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _get_related_carts(self):
        """Return the carts related to this transaction."""
        # We only consider sale orders with typology 'cart'
        return self.sale_order_ids.filtered(lambda so: so.typology == "cart")

    def _confirm_related_carts(self):
        """Confirm the carts related to this transaction."""
        self._get_related_carts().action_confirm_cart()

    def _set_authorized(self, state_message=None):
        """Override to set typology to sale when payment is authorized."""
        self._confirm_related_carts()
        return super()._set_authorized(state_message=state_message)

    def _set_pending(self, state_message=None):
        """Override to set typology to cart when payment is pending."""
        self._confirm_related_carts()
        return super()._set_pending(state_message=state_message)

    def _set_done(self, state_message=None):
        """Override to set typology to sale when payment is done."""
        self._confirm_related_carts()
        return super()._set_done(state_message=state_message)
