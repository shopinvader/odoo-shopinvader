# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from mock import Mock
from odoo.addons.payment_gateway_paypal.tests.test_payment import (
    PaypalCommonCase,
    PaypalScenario,
)
from odoo.addons.shopinvader.tests.common import CommonMixin


class ShopinvaderPaypalCase(PaypalCommonCase, CommonMixin, PaypalScenario):
    def setUp(self, *args, **kwargs):
        super(ShopinvaderPaypalCase, self).setUp(*args, **kwargs)
        CommonMixin.setUp(self)
        self.shopinvader_session = {"cart_id": self.sale.id}
        self.partner = self.sale.partner_id
        self.env["shopinvader.partner"].create(
            {
                "record_id": self.partner.id,
                "external_id": "ZG9kbw==",
                "backend_id": self.backend.id,
            }
        )
        self.sale.write(
            {"typology": "cart", "shopinvader_backend_id": self.backend.id}
        )
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="cart")
        self.cr.commit = Mock()  # Do not commit

    def _expected_return_url(self):
        # based on the backend information odoo will generate the
        # return url
        return self.backend.location + "/invader/cart/check_payment/paypal"

    def _create_transaction(self, **REDIRECT_URL):
        params = REDIRECT_URL.copy()
        params["action"] = "create"
        response = self.service.dispatch(
            "add_payment",
            params={
                "payment_mode": {"id": self.account_payment_mode.id},
                "paypal": params,
            },
        )
        self.assertEqual(response, {"redirect_to": "https://redirect"})
        transaction = self.sale.transaction_ids
        self.assertEqual(len(transaction), 1)
        return transaction

    def _simulate_return(self, transaction_id):
        response = self.service.dispatch(
            "check_payment",
            params={"paymentId": transaction_id, "provider_name": "paypal"},
        )
        return response

    def _check_successfull_return(self, transaction, result):
        super(ShopinvaderPaypalCase, self)._check_successfull_return(
            transaction, result
        )
        self.assertEqual(result["redirect_to"], "https://ThanksYou.com")

    def _check_failing_return(self, transaction, result):
        super(ShopinvaderPaypalCase, self)._check_failing_return(
            transaction, result
        )
        self.assertEqual(
            result["redirect_to"],
            "https://IamGoingToKickYourAssIfYouDoNotPaid.com",
        )
