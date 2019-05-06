# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from os.path import dirname

from mock import Mock
from odoo.addons.payment_gateway.tests.common import PaymentScenarioType
from odoo.addons.payment_gateway_stripe.tests.test_payment import (
    StripeCommonCase,
    StripeScenario,
)
from odoo.addons.shopinvader.tests.common import CommonMixin

REDIRECT_URL = {
    "redirect_cancel_url": "https://IamGoingToKickYourAssIfYouDoNotPaid.com",
    "redirect_success_url": "https://ThanksYou.com",
}


class ShopinvaderStripeCase(StripeCommonCase, CommonMixin, StripeScenario):
    __metaclass__ = PaymentScenarioType
    _test_path = dirname(__file__)

    def setUp(self, *args, **kwargs):
        super(ShopinvaderStripeCase, self).setUp(*args, **kwargs)
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

    def _create_transaction(self, card):
        params = REDIRECT_URL.copy()
        params["token"] = self._get_source(card)["id"]
        response = self.service.dispatch(
            "add_payment",
            params={
                "payment_mode": {"id": self.account_payment_mode.id},
                "stripe": params,
            },
        )
        transaction = self.sale.transaction_ids
        self.assertEqual(len(transaction), 1)
        self.assertEqual(
            self.sale.workflow_process_id,
            self.account_payment_mode.workflow_process_id,
        )
        return response, transaction, json.loads(transaction.data)

    def _check_reponse(self, response, redirect=False):
        self.assertIn("store_cache", response)
        self.assertIn("last_sale", response["store_cache"])
        if redirect:
            self.assertEqual(
                response["redirect_to"], REDIRECT_URL["redirect_success_url"]
            )
        else:
            self.assertNotIn("redirect_to", response)

    def _simulate_return(self, transaction):
        return self.service.dispatch(
            "check_payment",
            params={
                "source": transaction.external_id,
                "provider_name": "stripe",
            },
        )

    def _test_3d(self, card, success=True, mode="return"):
        response, transaction, source = self._create_transaction(card)
        self.assertEqual(response["redirect_to"], transaction.url)
        self.assertEqual(transaction.state, "pending")
        self._fill_3d_secure(transaction, success=success)
        if mode == "webhook":
            self._simulate_webhook(transaction)
            if success:
                self._check_captured(transaction)
            else:
                self.assertEqual(transaction.state, "failed")
        else:
            response = self._simulate_return(transaction)
            if success:
                self._check_captured(transaction)
                self._check_reponse(response, redirect=True)
            else:
                self.assertEqual(transaction.state, "failed")
                self.assertEqual(
                    response["redirect_to"],
                    REDIRECT_URL["redirect_cancel_url"],
                )
                self.assertIn("store_cache", response)
                self.assertIn("notifications", response["store_cache"])

    def _test_card(self, card, **kwargs):
        response, transaction, source = self._create_transaction(card)
        self._check_captured(transaction, **kwargs)
        self._check_reponse(response)

    def test_create_transaction_3d_not_supported(self):
        response, transaction, source = self._create_transaction(
            "378282246310005"
        )
        self._check_captured(transaction)
        self._check_reponse(response)
