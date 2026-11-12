# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _get_related_carts(self):
        """Add quotations related to this transaction."""
        carts = super()._get_related_carts()
        carts |= self.sale_order_ids.filtered(lambda so: so.typology == "quote")
        return carts
