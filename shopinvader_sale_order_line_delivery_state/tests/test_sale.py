# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader.tests.common import CommonCase


class TestSalesService(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.shop_sales = cls.env.ref("shopinvader.sale_order_2")

    def _get_service(self):
        work_ctx = dict(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        )
        with self.work_on_services(**work_ctx) as work:
            return work.component(usage="sales")

    def test_state_unprocessed(self):
        self.shop_sales.action_confirm()
        service = self._get_service()
        res = service.search()
        states = sorted(
            [x["delivery_state"] for x in res["data"][0]["lines"]["items"]]
        )
        self.assertEqual(
            states, ["shipping_unprocessed", "shipping_unprocessed"]
        )

    def test_state_partial(self):
        self.shop_sales.action_confirm()
        line = self.shop_sales.order_line[0]
        line.qty_delivered = 1.0
        service = self._get_service()
        res = service.search()
        states = sorted(
            [x["delivery_state"] for x in res["data"][0]["lines"]["items"]]
        )
        self.assertEqual(
            states, ["shipping_partially", "shipping_unprocessed"]
        )

    def test_state_done(self):
        self.shop_sales.action_confirm()
        line = self.shop_sales.order_line[0]
        line.qty_delivered = line.product_uom_qty
        service = self._get_service()
        res = service.search()
        states = sorted(
            [x["delivery_state"] for x in res["data"][0]["lines"]["items"]]
        )
        self.assertEqual(states, ["shipping_done", "shipping_unprocessed"])
