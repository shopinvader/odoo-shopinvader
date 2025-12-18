# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_search_engine_product_stock.tests.common import (
    StockCommonCase,
)


class TestShopinvaderApiWarehouseSaleChannelSearchEngineProductStock(StockCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.sale_channel = cls.env["sale.channel"].create(
            {
                "name": "Test Sale Channel",
            }
        )
        cls.sale_channel2 = cls.env["sale.channel"].create(
            {
                "name": "Test Sale Channel 2",
            }
        )

        cls.warehouse_1.sale_channel_ids = [(4, cls.sale_channel.id)]
        cls.warehouse_2.sale_channel_ids = [(4, cls.sale_channel2.id)]
        cls.index.backend_id.sale_channel_id = cls.sale_channel

    def test_warehouse_sync_1(self):
        self.assertEqual(self.index.warehouse_ids, self.warehouse_1)
        self.assertEqual(
            self.index.backend_id.sale_channel_id.warehouse_ids, self.warehouse_1
        )

        self.warehouse_1.sale_channel_ids = [
            (6, 0, (self.sale_channel | self.sale_channel2).ids)
        ]
        self.assertEqual(self.index.warehouse_ids, self.warehouse_1)

        self.warehouse_1.sale_channel_ids = [(4, self.sale_channel.id)]
        self.warehouse_2.sale_channel_ids = [
            (6, 0, (self.sale_channel | self.sale_channel2).ids)
        ]
        self.assertEqual(self.index.warehouse_ids, self.warehouse_1 | self.warehouse_2)
