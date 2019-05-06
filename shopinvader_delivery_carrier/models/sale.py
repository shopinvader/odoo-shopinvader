# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_available_carrier(self):
        self.ensure_one()
        return (
            self.shopinvader_backend_id.with_context(order_id=self.id)
            .carrier_ids.filtered("available")
            .sorted("price")
        )
