# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from .test_sale import CommonSaleCase


class TestSaleCancel(CommonSaleCase):
    def test_sale_cancel(self):
        self.sale.action_confirm()
        self.assertEqual("sale", self.sale.typology)
        self.assertEqual("sale", self.sale.state)

        self.service.dispatch("cancel", self.sale.id)

        self.assertEqual("cancel", self.sale.state)

    def test_sale_cancel_fail_if_delivered(self):
        self.sale.action_confirm()
        # deliver only 1 line
        self.sale.order_line[0].write({"qty_delivered": 1})
        self.env["sale.order.line"].flush(records=self.sale.order_line)
        with self.assertRaises(UserError):
            self.service.dispatch("cancel", self.sale.id)
        self.assertEqual("sale", self.sale.typology)
        self.assertEqual("sale", self.sale.state)

    def test_sale_cancel_to_cart(self):
        self.sale.action_confirm()
        self.assertEqual("sale", self.sale.typology)
        self.assertEqual("sale", self.sale.state)

        result = self.service.dispatch("reset_to_cart", self.sale.id)

        session = result.get("set_session")
        self.assertEqual("draft", self.sale.state)
        self.assertEqual("cart", self.sale.typology)
        self.assertIsInstance(session, dict)
        self.assertEqual(session.get("cart_id"), self.sale.id)
