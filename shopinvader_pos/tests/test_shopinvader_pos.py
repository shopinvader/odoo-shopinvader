# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields

from odoo.addons.shopinvader_v1_base.tests.common import CommonCase


class TestShopinvaderPos(CommonCase):
    """
    Tests for shopinvader.pos.service
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.PosOrder = cls.env["pos.order"]
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.pricelist = cls.env.ref("product.list0")
        cls.pick_type_out = cls.env["stock.picking.type"].search(
            [("code", "=", "outgoing")], limit=1
        )
        cls.product1 = cls.env.ref("product.product_product_4")
        cls.product2 = cls.env.ref("product.product_product_2")
        cls.pos_config = cls.env["pos.config"].create(
            {"name": "Test POS", "picking_type_id": cls.pick_type_out.id}
        )
        cls.pos_config.open_session_cb()
        amount_base = 1 * 100 + 12 * 30
        amount_tax = amount_base * 0.21
        amount_total = amount_base + amount_tax
        cls.pos_values = {
            "partner_id": cls.partner.id,
            "pricelist_id": cls.pricelist.id,
            "session_id": cls.pos_config.current_session_id.id,
            "amount_tax": amount_tax,
            "amount_total": amount_total,
            "amount_paid": 0,
            "amount_return": 0,
            "lines": [
                (
                    0,
                    False,
                    {
                        "name": "Test line 1",
                        "qty": 1,
                        "price_unit": 100,
                        "product_id": cls.product1.id,
                        "price_subtotal": 1 * 100,
                        "price_subtotal_incl": 1 * 100 * 1.21,
                    },
                ),
                (
                    0,
                    False,
                    {
                        "name": "Test line 2",
                        "qty": 12,
                        "price_unit": 30,
                        "product_id": cls.product2.id,
                        "price_subtotal": 12 * 30,
                        "price_subtotal_incl": 12 * 30 * 1.21,
                    },
                ),
            ],
        }
        cls.pos_order1 = cls.PosOrder.create(cls.pos_values)
        cls.pos_order2 = cls.PosOrder.create(cls.pos_values)
        cls.pos_order1.write({"state": "done"})
        cls.pos_order2.write({"state": "done"})

    def setUp(self):
        super().setUp()
        usage = "point_of_sale"
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage=usage)
        with self.work_on_services(
            shopinvader_session=self.shopinvader_session
        ) as work:
            self.service_guest = work.component(usage=usage)

    def _build_json(self, pos_order):
        result = {
            "pos_id": pos_order.id,
            "amount_untaxed": pos_order.amount_total - pos_order.amount_tax,
            "name": pos_order.name,
            "reference": pos_order.pos_reference or None,
            "amount_tax": pos_order.amount_tax,
            "date": fields.Datetime.to_string(pos_order.date_order),
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
        expected_result = [self._build_json(pos_order) for pos_order in pos_orders]
        for result, expected in zip(result_data, expected_result):
            self.assertDictEqual(result, expected)

    def test_get1(self):
        pos_order = self.pos_order1
        result = self.service.dispatch("get", pos_order.id)
        result_data = result.get("data", {})
        expected_result = self._build_json(pos_order)
        self.assertDictEqual(result_data, expected_result)
