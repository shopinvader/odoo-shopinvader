# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models
import logging
_logger = logging.getLogger(__name__)

try:
    from slugify import slugify
except (ImportError, IOError) as err:
    _logger.debug(err)


class ShopinvaderBackend(models.Model):
    _inherit = 'shopinvader.backend'

    warehouse_ids = fields.Many2many(
        "stock.warehouse",
        default=lambda self: self._default_warehouse_field(),
        required=True,
    )
    product_stock_field_id = fields.Many2one(
        "ir.model.fields",
        "Product stock field",
        domain=[
            ('ttype', 'in', ['float', 'integer']),
            ('model_id.model', '=', 'product.product'),
            ('name', 'in', ('qty_available', 'virtual_available')),
        ],
        help="Field used to have the current stock of a product.product",
        default=lambda self: self._default_stock_field(),
    )

    def _default_stock_field(self):
        return self.env.ref('stock.field_product_product_qty_available')

    def _default_warehouse_field(self):
        return self.env['stock.warehouse'].search([], limit=1)

    def _get_warehouse(self):
        self.ensure_one()
        result = {'global': self.warehouse_ids.ids}
        if len(self.warehouse_ids) > 1:
            for warehouse in self.warehouse_ids:
                result[slugify(warehouse.code)] = [warehouse.id]
        return result
