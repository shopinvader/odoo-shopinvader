# Copyright 2020 Camptocamp SA
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader_restapi.tests.common import CommonCase

from .common import CommonPackagingCase


class TestSaleOrderPackaging(CommonCase, CommonPackagingCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale = cls.env.ref("shopinvader_restapi.sale_order_2")
        cls.sale_line1 = cls.env.ref("shopinvader_restapi.sale_order_line_4")
        cls.sale_line2 = cls.env.ref("shopinvader_restapi.sale_order_line_5")
        cls.pkg_box = cls.env["product.packaging"].create(
            {
                "name": "Box",
                "packaging_level_id": cls.pkg_level_retail_box.id,
                "product_id": cls.sale_line1.product_id.id,
                "qty": 100,
                "barcode": "BOX",
            }
        )
        cls.sale_line1.write(
            {"product_packaging_id": cls.pkg_box.id, "product_packaging_qty": 5}
        )
        cls.sale.action_confirm()
        cls.partner = cls.env.ref("shopinvader_restapi.partner_1")

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
                        "name": self.pkg_box.packaging_level_id.name,
                        "code": self.pkg_box.packaging_level_id.code,
                        "barcode": self.pkg_box.barcode,
                    },
                )
                self.assertEqual(line["packaging_qty"], 5)
                self.assertEqual(line["qty"], 500)
            elif line["id"] == self.sale_line2.id:
                self.assertEqual(line["packaging"], None)
                self.assertEqual(line["packaging_qty"], 0.0)
                self.assertEqual(line["qty"], self.sale_line2.product_uom_qty)
