# Copyright 2020 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import tagged

from odoo.addons.shopinvader_schema_sale.schemas import Sale

from .common import TestShopinvaderDeliveryCarrierCommon


@tagged("post_install", "-at_install")
class TestSaleDeliveries(TestShopinvaderDeliveryCarrierCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product_model = cls.env["product.product"]
        product = product_model.create({"name": "Unittest P1", "type": "product"})
        cls.cart.order_line[0].product_id = product
        cls.stock_loc = cls.env.ref("stock.stock_location_stock")
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.wh_main = cls.env.ref("stock.warehouse0")
        cls.env["stock.quant"]._update_available_quantity(product, cls.stock_loc, 10)

    def _confirm_and_deliver_sale(self):
        self.cart.action_confirm()
        picking = self.cart.picking_ids
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids._action_done()

    def test_read_sale(self):
        self.cart.action_confirm_cart()
        self._confirm_and_deliver_sale()
        schema = Sale.from_sale_order(self.cart)
        pick = self.cart.picking_ids[0]
        self.assertEqual(schema.delivery.pickings[0].delivery_id, pick.id)
        self.assertEqual(schema.delivery.pickings[0].name, pick.name)
        self.assertEqual(schema.delivery.pickings[0].delivery_date, pick.scheduled_date)
