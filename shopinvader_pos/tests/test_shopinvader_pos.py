# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.shopinvader.tests.common import CommonCase


class TestShopinvaderPos(CommonCase):
    """
    Tests for shopinvader.pos.service
    """

    def setUp(self):
        super(TestShopinvaderPos, self).setUp()
        self.env = self.env(
            context=dict(self.env.context, tracking_disable=True)
        )
        self.PosOrder = self.env["pos.order"]
        self.partner = self.env.ref("base.res_partner_2")
        self.pricelist = self.env.ref("product.list0")
        self.pick_type_out = self.env.ref("point_of_sale.picking_type_posout")
        self.product1 = self.env.ref("product.product_product_4")
        self.product2 = self.env.ref("product.product_product_2")
        self.pos_config = self.env["pos.config"].create(
            {"name": "Test POS", "picking_type_id": self.pick_type_out.id}
        )
        self.pos_config.open_session_cb()
        self.pos_values = {
            "partner_id": self.partner.id,
            "pricelist_id": self.pricelist.id,
            "session_id": self.pos_config.current_session_id.id,
            "lines": [
                (
                    0,
                    False,
                    {
                        "name": "Test line 1",
                        "qty": 1,
                        "price_unit": 100,
                        "product_id": self.product1.id,
                    },
                ),
                (
                    0,
                    False,
                    {
                        "name": "Test line 2",
                        "qty": 12,
                        "price_unit": 30,
                        "product_id": self.product2.id,
                    },
                ),
            ],
        }
        usage = "point_of_sale"
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage=usage)
        with self.work_on_services(
            shopinvader_session=self.shopinvader_session
        ) as work:
            self.service_guest = work.component(usage=usage)
        self.pos_order1 = self.PosOrder.create(self.pos_values)
        self.pos_order2 = self.PosOrder.create(self.pos_values)
        self.pos_order1.action_pos_order_done()
        self.pos_order2.action_pos_order_done()

    def _build_json(self, pos_order):
        result = {
            "pos_id": pos_order.id,
            "amount_untaxed": pos_order.amount_total - pos_order.amount_tax,
            "name": pos_order.name,
            "reference": pos_order.pos_reference or None,
            "amount_tax": pos_order.amount_tax,
            "location": {
                "location_id": pos_order.location_id.id,
                "name": pos_order.location_id.name,
            },
            "date": pos_order.date_order,
            "partner": {
                "partner_id": pos_order.partner_id.id,
                "name": pos_order.partner_id.name,
            },
            "amount_total": pos_order.amount_total,
        }
        return result

    def test_search1(self):
        result = self.service.dispatch("search")
        result_data = result.get("data", {})
        pos_orders = self.pos_order2 | self.pos_order1
        expected_result = [
            self._build_json(pos_order) for pos_order in pos_orders
        ]
        for result, expected in zip(result_data, expected_result):
            self.assertDictEqual(result, expected)

    def test_get1(self):
        pos_order = self.pos_order1
        result = self.service.dispatch("get", pos_order.id)
        result_data = result.get("data", {})
        expected_result = self._build_json(pos_order)
        self.assertDictEqual(result_data, expected_result)
