# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase


class TestSale(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("shopinvader.partner_1")

    def setUp(self, *args, **kwargs):
        super(TestSale, self).setUp(*args, **kwargs)
        with self.work_on_services(partner=self.partner) as work:
            self.service = work.component(usage="sales")

    def test_sale_order_info(self):
        online_information_for_customer = "TEST"
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "online_information_for_customer": online_information_for_customer,
                "shopinvader_backend_id": self.env.ref(
                    "shopinvader.backend_1"
                ).id,
            }
        )
        so.action_confirm()
        res = self.service.get(so.id)
        self.assertEqual(
            res.get("online_information_for_customer"),
            so.online_information_for_customer,
        )
