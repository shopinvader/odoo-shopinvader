# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase


class TestCart(CommonConnectedCartCase):
    def setUp(self):
        super().setUp()
        # Disable all existing exception rules, to avoid noise.
        # Unexpected demo-data can be nasty.
        self.env["exception.rule"].search([]).write({"active": False})
        # Enable the one we want to test
        self.exception = self.env.ref("sale_exception.exception_partner_sale_warning")
        self.exception.active = True
        self.cart.partner_id.sale_warn = "warning"

    def test_cart(self):
        # Case 1: Blocked
        data = self.service.dispatch("check_exceptions")
        self.assertTrue(self.cart.exception_ids)
        self.assertEqual(data[0]["name"], self.exception.name)
        # Case 2: Unblocked
        self.cart.partner_id.sale_warn = False
        data = self.service.dispatch("check_exceptions")
        self.assertFalse(self.cart.exception_ids)
        self.assertFalse(data)
