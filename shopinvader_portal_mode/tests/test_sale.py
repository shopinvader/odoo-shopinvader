# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader.tests.common import CommonCase


class TestSalesService(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.shop_sales = cls.env.ref("shopinvader.sale_order_2")
        cls.shop_sales += cls.shop_sales.copy()
        cls.shop_sales.action_confirm()
        cls.shop_sales.write(
            {"typology": "sale", "shopinvader_backend_id": cls.backend.id}
        )
        cls.non_shop_sales = cls.env.ref("shopinvader.sale_order_2")
        cls.non_shop_sales.shopinvader_backend_id = False
        cls.non_shop_sales += cls.non_shop_sales.copy()
        cls.non_shop_sales.action_confirm()
        cls.non_shop_sales.write(
            {"typology": "sale", "shopinvader_backend_id": cls.backend.id}
        )
        cls.partner = cls.env.ref("shopinvader.partner_1")

    def _get_service(self):
        work_ctx = dict(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        )
        with self.work_on_services(**work_ctx) as work:
            return work.component(usage="sales")

    def test_list_sale_default(self):
        service = self._get_service()
        res = service.search()
        self.assertEqual(
            len(res["data"]),
            self.env["sale.order"].search_count(
                [
                    ("partner_id", "=", self.partner.id),
                    ("shopinvader_backend_id", "=", self.backend.id),
                ]
            ),
        )

    def test_list_sale_portal_mode(self):
        self.backend.sale_order_portal_mode = True
        service = self._get_service()
        res = service.search()
        self.assertEqual(
            len(res["data"]),
            self.env["sale.order"].search_count(
                [("partner_id", "=", self.partner.id)]
            ),
        )
