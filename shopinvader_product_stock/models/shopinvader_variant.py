# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from slugify import slugify


class ShopinvaderVariant(models.Model):
    _inherit = 'shopinvader.variant'

    stock_data = fields.Serialized(compute='_compute_stock_data')

    def _get_stock_key(self):
        self.ensure_one()
        line = self.env['ir.exports.line'].search([
            ('export_id', '=', self.index_id.exporter_id.id),
            ('name', '=', 'stock_data'),
            ])
        if line.alias:
            return line.alias.split(':')[1]
        else:
            return line.name

    def _get_warehouse(self):
        result = {'global': self.backend_id.warehouse_ids.ids}
        self.ensure_one()
        if len(self.backend_id.warehouse_ids) > 1:
            for warehouse in self.backend_id.warehouse_ids:
                result[slugify(warehouse.code)] = [warehouse.id]
        return result

    def _prepare_stock_data(self):
        stock_key = self.backend_id.product_stock_field_id.name
        return {'qty': self[stock_key]}

    def _compute_stock_data(self):
        for record in self:
            data = {}
            for wh_key, wh_ids in record._get_warehouse().items():
                data[wh_key] = record.with_context(warehouse=wh_ids)\
                    ._prepare_stock_data()
            record.stock_data = data
