# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase


class SaleCase(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product_model = cls.env["product.product"]
        product = product_model.create(
            {"name": "Unittest P1", "type": "product"}
        )
        cls.sale = cls.env.ref("shopinvader.sale_order_2")
        cls.sale.order_line[0].product_id = product
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.stock_loc = cls.env.ref("stock.stock_location_stock")
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.wh_main = cls.env.ref("stock.warehouse0")
        cls.env["stock.quant"]._update_available_quantity(
            product, cls.stock_loc, 10
        )

        with cls.work_on_services(cls, partner=cls.partner) as work:
            cls.service = work.component(usage="sales")

    def _confirm_and_deliver_sale(self):
        self.sale.action_confirm()
        picking = self.sale.picking_ids
        picking.action_confirm()
        picking.action_assign()
        picking.move_lines._action_done()

    def test_read_sale(self):
        self.sale.action_confirm_cart()
        self._confirm_and_deliver_sale()
        res = self.service.get(self.sale.id)
        pick = self.sale.picking_ids[0]
        self.assertEqual(
            res["deliveries"][0],
            {"id": pick.id, "name": pick.name, "date": pick.scheduled_date},
        )
