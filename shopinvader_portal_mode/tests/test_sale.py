# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import PortalModeCommonCase


class TestSalesService(PortalModeCommonCase):
    def test_list_sale_default(self):
        service = self._get_service("sales")
        res = service.search()
        res_ids = sorted([x["id"] for x in res["data"]])
        self.assertTrue(
            "draft"
            not in self.env["sale.order"].browse(res_ids).mapped("state")
        )
        self.assertEqual(res_ids, sorted(self.shop_sales.ids))

    def test_list_sale_portal_mode(self):
        self.backend.sale_order_portal_mode = True
        service = self._get_service("sales")
        res = service.search()
        res_ids = sorted([x["id"] for x in res["data"]])
        self.assertTrue(
            "draft"
            not in self.env["sale.order"].browse(res_ids).mapped("state")
        )
        self.assertEqual(
            res_ids, sorted((self.shop_sales + self.non_shop_sales).ids)
        )
