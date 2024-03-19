# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.sale_cart.tests.test_sale_cart import TestSaleCart as TestSaleCartBase


class TestSaleCart(TestSaleCartBase):
    def test_transfer_cart(self):
        product_2 = self.env["product.product"].create(
            {"name": "product", "uom_id": self.env.ref("uom.product_uom_unit").id}
        )
        partner_2 = self.env["res.partner"].create({"name": "partner 2"})
        so_cart_2 = self.env["sale.order"].create(
            {
                "partner_id": partner_2.id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 1}),
                    (0, 0, {"product_id": product_2.id, "product_uom_qty": 1}),
                ],
                "typology": "cart",
            }
        )
        merged_cart = so_cart_2._transfer_cart(self.partner.id)
        self.assertEqual(merged_cart.id, self.so_cart.id)
        self.assertEqual(len(merged_cart.order_line), 2)
        self.assertEqual(
            merged_cart.order_line.filtered(
                lambda l, product=self.product: l.product_id.id == product.id
            ).product_uom_qty,
            2,
        )
        self.assertEqual(
            merged_cart.order_line.filtered(
                lambda l, product=product_2: l.product_id.id == product.id
            ).product_uom_qty,
            1,
        )
        self.assertFalse(so_cart_2.exists())
