# Copyright 2020 Camptocamp SA
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader.tests.common import CommonCase


class TestSaleOrderPackaging(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale = cls.env.ref("shopinvader.sale_order_2")
        cls.sale_line1 = cls.env.ref("shopinvader.sale_order_line_4")
        cls.sale_line2 = cls.env.ref("shopinvader.sale_order_line_5")
        cls.pkg_box = cls.env["product.packaging"].create(
            {
                "name": "Box",
                "product_id": cls.sale_line1.product_id.id,
                "qty": 100,
            }
        )
        cls.sale_line1.write(
            {"product_packaging": cls.pkg_box.id, "product_packaging_qty": 5}
        )
        cls.sale.action_confirm()
        cls.partner = cls.env.ref("shopinvader.partner_1")
        # This module adds new keys: recompute
        cls._refresh_json_data(cls, cls.sale.mapped("order_line.product_id"))

    def setUp(self):
        super().setUp()
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="sales")

    def test_sale_line_data(self):
        res = self.service.search()
        sale = res["data"][0]
        for line in sale["lines"]["items"]:
            if line["id"] == self.sale_line1.id:
                self.assertEqual(
                    line["packaging"],
                    {
                        "id": self.pkg_box.id,
                        "name": self.pkg_box.packaging_type_id.name,
                        "code": self.pkg_box.packaging_type_id.code,
                    },
                )
                self.assertEqual(line["packaging_qty"], 5)
                self.assertEqual(line["qty"], 500)
            elif line["id"] == self.sale_line2.id:
                self.assertEqual(line["packaging"], None)
                self.assertEqual(line["packaging_qty"], 0.0)
                self.assertEqual(line["qty"], self.sale_line2.product_uom_qty)
            self.assertIn("sell_only_by_packaging", line["product"])
