# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ShopinvaderVariant(models.Model):
    _inherit = 'shopinvader.variant'

    stock_data = fields.Serialized(compute='_compute_stock_data')

    def _prepare_stock_data(self):
        stock_key = self.backend_id.product_stock_field_id.name
        return {'global': {'qty': self[stock_key]}}

    def _compute_stock_data(self):
        for record in self:
            record.stock_data = record._prepare_stock_data()
