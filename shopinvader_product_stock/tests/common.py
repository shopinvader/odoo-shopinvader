# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.queue_job.tests.common import JobMixin
from odoo.addons.connector_search_engine.tests.common import TestSeBackendCase


class StockCommonCase(TestSeBackendCase, JobMixin):

    def setUp(self):
        super(StockCommonCase, self).setUp()
        ref = self.env.ref
        self.shopinvader_backend = ref('shopinvader.backend_1')
        self.warehouse_1 = ref('stock.warehouse0')
        self.loc_1 = self.warehouse_1.lot_stock_id
        self.warehouse_2 = ref('stock.stock_warehouse_shop0')
        self.loc_2 = self.warehouse_2.lot_stock_id
        self.product = ref('product.product_product_4')
        self.shopinvader_backend.bind_all_product()
        self.index = self.env['se.index'].create({
            'name': 'test-product-index',
            'backend_id': self.se_backend.se_backend_id.id,
            'exporter_id': ref('shopinvader.ir_exp_shopinvader_variant').id,
            'lang_id': ref('base.lang_en').id,
            'model_id': ref('shopinvader.model_shopinvader_variant').id,
            })
        self.shopinvader_backend.write({
            'se_backend_id': self.se_backend.se_backend_id.id,
            'warehouse_ids': [(6, 0, self.warehouse_1.ids)],
            'product_stock_field_id':
                ref("stock.field_product_product_qty_available").id,
        })

    def _add_stock_to_product(self, product, location, qty):
        """
        Set the stock quantity of the product
        :param product: product.product recordset
        :param qty: float
        """
        wizard = self.env['stock.change.product.qty'].create({
            'product_id': product.id,
            'new_quantity': qty,
            'location_id': location.id,
        })
        wizard.change_product_qty()
