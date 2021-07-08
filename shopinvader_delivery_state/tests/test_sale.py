# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader.tests.common import CommonCase


class TestSalesService(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.shop_sales = cls.env.ref("shopinvader.sale_order_2")
        cls.shop_sales += cls.shop_sales.copy()

    def _get_service(self):
        work_ctx = dict(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        )
        with self.work_on_services(**work_ctx) as work:
            return work.component(usage="sales")

    def test_state_default(self):
        service = self._get_service()
        res = service.search()
        states = sorted([x["state"] for x in res["data"]])
        self.assertEqual(states, ["pending"] * len(res["data"]))

    def test_state_unprocessed(self):
        self.shop_sales.action_confirm()
        service = self._get_service()
        res = service.search()
        states = sorted([x["state"] for x in res["data"]])
        self.assertEqual(states, ["shipping_unprocessed"] * len(res["data"]))

    def test_state_partial(self):
        self.shop_sales.action_confirm()
        line = self.shop_sales[0].order_line[0]
        line.qty_delivered = line.product_uom_qty
        service = self._get_service()
        res = service.search()
        states = sorted([x["state"] for x in res["data"]])
        self.assertEqual(
            states, ["shipping_partially", "shipping_unprocessed"]
        )

    def test_state_done(self):
        self.shop_sales.action_confirm()
        for line in self.shop_sales[0].order_line:
            line.qty_delivered = line.product_uom_qty
        service = self._get_service()
        res = service.search()
        states = sorted([x["state"] for x in res["data"]])
        self.assertEqual(states, ["shipping_done", "shipping_unprocessed"])

    def test_state_done_not_shipped(self):
        self.shop_sales.action_confirm()
        self.shop_sales[0].action_done()
        service = self._get_service()
        res = service.search()
        states = sorted([x["state"] for x in res["data"]])
        self.assertEqual(
            states, ["shipping_unprocessed", "shipping_unprocessed"]
        )
