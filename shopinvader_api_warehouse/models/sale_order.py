# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _confirm_cart(self):
        rv = super()._confirm_cart()
        self.partner_id.shopinvader_default_warehouse_id = self.warehouse_id
        return rv
