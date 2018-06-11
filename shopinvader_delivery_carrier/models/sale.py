# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_available_carrier(self):
        self.ensure_one()
        return self.shopinvader_backend_id.with_context(
            order_id=self.id).carrier_ids.filtered('available').sorted('price')

    def _set_default_carrier(self):
        carriers = self._get_available_carrier()
        if carriers:
            self.carrier_id = carriers[0]
            self.delivery_set()
