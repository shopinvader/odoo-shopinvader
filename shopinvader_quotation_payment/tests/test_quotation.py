# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase
from odoo.addons.shopinvader_quotation.tests.test_quotation import (
    CommonConnectedQuotationCase,
)
from odoo.exceptions import UserError


class ShopinvaderCartNoPaymentCase(CommonConnectedCartCase):
    def test_get_no_cart_payment_info(self):
        self.cart.order_line[0].product_id.only_quotation = True
        response = self.service.dispatch("search")
        self.assertEqual(
            response["data"]["payment"]["available_methods"]["count"], 0
        )


class ShopinvaderQuotationPaymentCase(CommonConnectedQuotationCase):
    def setUp(self, *args, **kwargs):
        super(ShopinvaderQuotationPaymentCase, self).setUp(*args, **kwargs)
        self.account_payment_mode = self.env.ref(
            "shopinvader_payment.payment_method_check"
        )
        self.cart.write({"payment_mode_id": self.account_payment_mode.id})

    def test_get_cart_payment_info(self):
        self.cart.order_line[0].product_id.only_quotation = True
        response = self.service.dispatch("search", params={"id": self.cart.id})
        self.assertIn("available_methods", response["data"][0]["payment"])
        self.assertEqual(
            response["data"][0]["payment"]["available_methods"]["count"],
            len(self.backend.payment_method_ids),
        )

    def test_wrong_state_payment(self):
        self.assertEqual(self.cart.typology, "quotation")
        with self.assertRaises(UserError):
            self.service.dispatch(
                "add_payment",
                self.cart.id,
                params={"payment_mode": {"id": self.account_payment_mode.id}},
            )
        self.assertEqual(self.cart.typology, "quotation")

    def test_add_check_payment(self):
        self.assertEqual(self.cart.typology, "quotation")
        self.cart.state = "sent"
        self.service.dispatch(
            "add_payment",
            self.cart.id,
            params={"payment_mode": {"id": self.account_payment_mode.id}},
        )
        self.assertEqual(
            self.cart.workflow_process_id,
            self.account_payment_mode.workflow_process_id,
        )
        self.assertEqual(self.cart.typology, "sale")
