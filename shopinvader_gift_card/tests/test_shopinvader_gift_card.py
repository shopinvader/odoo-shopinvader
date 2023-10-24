# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from freezegun import freeze_time

from odoo.addons.datamodel.tests.common import SavepointDatamodelCase
from odoo.addons.gift_card.tests.common import TestGiftCardCommon
from odoo.addons.shopinvader.tests.common import NotificationCaseMixin
from odoo.addons.shopinvader.tests.test_sale import CommonSaleCase


class ShopinvaderGiftcardTest(
    CommonSaleCase, TestGiftCardCommon, SavepointDatamodelCase, NotificationCaseMixin
):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        self.gift_card_journal = self.env.ref("gift_card.gift_card_journal")
        self.cart = self.env.ref("shopinvader.sale_order_2")
        self.acquirer = self.env.ref(
            "account_payment_gift_card.payment_acquirer_gift_card"
        )
        shopinvader_session = {"cart_id": self.cart.id}

        self.gc1 = self.env["gift.card"].create(
            {
                "initial_amount": 100,
                "is_divisible": True,
                "duration": 0,
                "buyer_id": self.cart.partner_id.id,
                "gift_card_tmpl_id": self.env.ref("gift_card.product_gift_card").id,
            }
        )

        with self.work_on_services(
            partner=None, shopinvader_session=shopinvader_session
        ) as work:
            self.cart_service = work.component(usage="cart")
            self.gift_card = work.component(usage="gift_card")

    def selling_gift_card(self, date):
        params = {
            "product_id": self.product_gift_card.id,
            "item_qty": 1,
            "initial_amount": 250,
            "start_date": date,
            "comment": "comment test",
            "beneficiary_id": self.partner.id,
            "beneficiary_name": "for you",
            "beneficiary_email": "for@you.com",
            "buyer_id": self.partner,
            "buyer_name": "from me",
            "buyer_email": "from@me.com",
            "gift_card_tmpl_id": self.template_gift_card,
            "shopinvader_backend_id": self.backend.id,
        }

        self.cart_service.dispatch("add_item", params=params)
        self.cart.action_confirm_cart()
        self.cart.action_confirm()
        invoice = self.cart._create_invoices()
        return invoice

    def test_1_sale_and_create_gift_card(self):
        nb_gift_cards = len(self.env["gift.card"].search([]))
        today = datetime.date.today().isoformat()
        invoice = self.selling_gift_card(today)
        self.assertEqual(self.cart.order_line[2].price_unit, 250)
        gift_card = self.cart.order_line[2].gift_card_id
        self.assertTrue(gift_card)
        self.assertTrue(gift_card.state, "draft")
        invoice.action_post()

        self.assertEqual(len(self.env["gift.card"].search([])), nb_gift_cards + 1)
        self.assertTrue(gift_card.state, "active")

    def test_2_gift_card_notifications(self):
        self.cart.user_id.email = "email@email.com"
        self._init_job_counter()
        today = datetime.date.today().isoformat()
        invoice = self.selling_gift_card(today)
        invoice.action_post()
        gift_card = self.cart.order_line[2].gift_card_id
        self._check_nbr_job_created(5)
        self._perform_created_job()
        self._check_notification("gift_card_created", gift_card)
        self._check_notification("gift_card_activated", gift_card)

    def test_3_cron_email_activation(self):
        invoice = self.selling_gift_card("2222-01-01")
        gift_card = self.cart.order_line[2].gift_card_id
        invoice.action_post()
        self._init_job_counter()
        self.env["gift.card"].cron_email_to_gift_card_beneficiary()
        self.assertEqual(gift_card.state, "not_activated")
        self.assertFalse(gift_card.email_confirmation_send)
        self._check_nbr_job_created(0)

        with freeze_time("2222-01-01"):
            self._init_job_counter()
            self.env["gift.card"].cron_email_to_gift_card_beneficiary()
            self.assertEqual(gift_card.state, "active")
            self.assertTrue(gift_card.email_confirmation_send)
            self._check_nbr_job_created(1)

    def test_4_sale_several_gift_cards(self):
        today = datetime.date.today().isoformat()
        params_1 = {
            "product_id": self.product_gift_card.id,
            "item_qty": 1,
            "initial_amount": 250,
            "start_date": today,
            "comment": "comment test",
            "beneficiary_id": self.partner.id,
            "beneficiary_name": "for you",
            "beneficiary_email": "for@you.com",
            "buyer_id": self.partner,
            "buyer_name": "from me",
            "buyer_email": "from@me.com",
            "gift_card_tmpl_id": self.template_gift_card,
            "shopinvader_backend_id": self.backend.id,
        }
        params_2 = {
            "product_id": self.product_gift_card.id,
            "item_qty": 1,
            "initial_amount": 200,
            "start_date": today,
            "comment": "comment test",
            "beneficiary_id": self.partner.id,
            "beneficiary_name": "for you",
            "beneficiary_email": "for@you.com",
            "buyer_id": self.partner,
            "buyer_name": "from me",
            "buyer_email": "from@me.com",
            "gift_card_tmpl_id": self.template_gift_card,
            "shopinvader_backend_id": self.backend.id,
        }
        nb_gift_cards = len(self.env["gift.card"].search([]))
        self.cart_service.dispatch("add_item", params=params_1)
        self.cart_service.dispatch("add_item", params=params_2)
        self.cart.action_confirm_cart()
        self.cart.action_confirm()
        self.assertEqual(self.cart.order_line[2].price_unit, 250)
        self.assertEqual(self.cart.order_line[3].price_unit, 200)
        self.assertEqual(len(self.env["gift.card"].search([])), nb_gift_cards + 2)
