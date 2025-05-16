# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
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
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create({"product_id": cls.product.id, "product_uom_qty": 1})
                ],
            }
        )

    def test_typology_default(self):
        self.assertEqual(self.sale_order.typology, "sale")
