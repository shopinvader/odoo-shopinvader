# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import psycopg2

from odoo import exceptions
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


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
        cls.cart = cls.env["sale.order"].create(
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
        cls.address_step = cls.env.ref("sale_cart_step.cart_step_address")
        cls.checkout_step = cls.env.ref("sale_cart_step.cart_step_checkout")
        cls.last_step = cls.env.ref("sale_cart_step.cart_step_last")

    def test_update_steps(self):
        self.assertFalse(self.cart.cart_step_id)
        self.assertFalse(self.cart.cart_step_done_ids)
        self.cart.cart_step_update(
            current_step=self.address_step.code, next_step=self.checkout_step.code
        )
        self.assertIn(self.address_step, self.cart.cart_step_done_ids)
        self.assertEqual(self.cart.cart_step_id, self.checkout_step)
        self.cart.cart_step_update(
            current_step=self.checkout_step.code, next_step=self.last_step.code
        )
        self.assertIn(self.checkout_step, self.cart.cart_step_done_ids)
        self.assertEqual(self.cart.cart_step_id, self.last_step)

    def test_update_steps_bad_code(self):
        with self.assertRaisesRegex(exceptions.UserError, "Invalid step code foo"):
            self.cart.cart_step_update(current_step="foo")

    @mute_logger("odoo.sql_db")
    def test_uniq(self):
        with self.assertRaises(psycopg2.errors.UniqueViolation):
            self.last_step.copy()
        self.last_step.active = False
        self.assertTrue(self.last_step.copy())
