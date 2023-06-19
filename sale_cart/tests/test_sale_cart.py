# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleCart(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleCart, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product = cls.env["product.product"].create(
            {
                "name": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "partner"})
        cls.so_cart = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {"product_id": cls.product.id, "product_uom_qty": 1},
                    )
                ],
                "typology": "cart",
            }
        )

    def test_action_confirm_cart(self):
        self.assertEqual("draft", self.so_cart.state)
        self.assertEqual("cart", self.so_cart.typology)
        self.so_cart.action_confirm_cart()
        self.assertEqual("draft", self.so_cart.state)
        self.assertEqual("sale", self.so_cart.typology)

    def test_action_confirm(self):
        self.assertEqual("draft", self.so_cart.state)
        self.assertEqual("cart", self.so_cart.typology)
        self.so_cart.action_confirm()
        self.assertEqual("sale", self.so_cart.state)
        self.assertEqual("sale", self.so_cart.typology)
