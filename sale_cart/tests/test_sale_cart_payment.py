# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.payment.tests.common import PaymentCommon

from .common import SaleCartCommon


class TestSaleCartPayment(SaleCartCommon, PaymentCommon):
    def test_action_confirm_cart_on_transaction_authorized(self):
        self.assertEqual("draft", self.so_cart.state)
        self.assertEqual("cart", self.so_cart.typology)
        transaction = self.env["payment.transaction"].create(
            {
                "amount": self.so_cart.amount_total,
                "currency_id": self.currency.id,
                "provider_id": self.provider.id,
                "reference": self.so_cart.name,
                "operation": "online_redirect",
                "partner_id": self.partner.id,
            }
        )
        self.so_cart.transaction_ids |= transaction
        self.provider.support_manual_capture = True
        transaction._set_authorized()
        self.assertEqual("sale", self.so_cart.typology)
        # The sale order is confirmed since a transaction with the right amount
        # is authorized
        self.assertEqual("sale", self.so_cart.state)

    def test_action_confirm_cart_on_transaction_pending(self):
        self.assertEqual("draft", self.so_cart.state)
        self.assertEqual("cart", self.so_cart.typology)
        transaction = self.env["payment.transaction"].create(
            {
                "amount": self.so_cart.amount_total,
                "currency_id": self.currency.id,
                "provider_id": self.provider.id,
                "reference": self.so_cart.name,
                "operation": "online_redirect",
                "partner_id": self.partner.id,
            }
        )
        self.so_cart.transaction_ids |= transaction
        transaction._set_pending()
        self.assertEqual("sale", self.so_cart.typology)
        # The sale order is set to 'sent' when a transaction is pending
        self.assertEqual("sent", self.so_cart.state)
        transaction._reconcile_after_done()
        self.assertEqual("sent", self.so_cart.state)

    def test_action_confirm_cart_on_transaction_done(self):
        self.assertEqual("draft", self.so_cart.state)
        self.assertEqual("cart", self.so_cart.typology)
        transaction = self.env["payment.transaction"].create(
            {
                "amount": self.so_cart.amount_total,
                "currency_id": self.currency.id,
                "provider_id": self.provider.id,
                "reference": self.so_cart.name,
                "operation": "online_redirect",
                "partner_id": self.partner.id,
            }
        )
        self.so_cart.transaction_ids |= transaction
        transaction._set_done()
        self.assertEqual("sale", self.so_cart.typology)
        # The sale order is not confirmed instantly on done
        self.assertEqual("draft", self.so_cart.state)
        # The sale order is confirmed after the post-processing
        transaction._reconcile_after_done()
        self.assertEqual("sale", self.so_cart.state)

    def test_action_confirm_cart_on_transaction_error(self):
        self.assertEqual("draft", self.so_cart.state)
        self.assertEqual("cart", self.so_cart.typology)
        transaction = self.env["payment.transaction"].create(
            {
                "amount": self.so_cart.amount_total,
                "currency_id": self.currency.id,
                "provider_id": self.provider.id,
                "reference": self.so_cart.name,
                "operation": "online_redirect",
                "partner_id": self.partner.id,
            }
        )
        self.so_cart.transaction_ids |= transaction
        transaction._set_error(state_message="Test error")
        # The sale order stays as a cart on error
        self.assertEqual("cart", self.so_cart.typology)
        # The sale order is not confirmed on error
        self.assertEqual("draft", self.so_cart.state)

    def test_action_confirm_cart_on_transaction_cancel(self):
        self.assertEqual("draft", self.so_cart.state)
        self.assertEqual("cart", self.so_cart.typology)
        transaction = self.env["payment.transaction"].create(
            {
                "amount": self.so_cart.amount_total,
                "currency_id": self.currency.id,
                "provider_id": self.provider.id,
                "reference": self.so_cart.name,
                "operation": "online_redirect",
                "partner_id": self.partner.id,
            }
        )
        self.so_cart.transaction_ids |= transaction
        transaction._set_canceled()
        # The sale order stays as a cart on cancel
        self.assertEqual("cart", self.so_cart.typology)
        # The sale order is not confirmed on cancel
        self.assertEqual("draft", self.so_cart.state)

    def test_action_confirm_cart_on_transaction_authorize_wrong_amount(self):
        self.assertEqual("draft", self.so_cart.state)
        self.assertEqual("cart", self.so_cart.typology)
        transaction = self.env["payment.transaction"].create(
            {
                "amount": self.so_cart.amount_total + 100,  # Wrong amount
                "currency_id": self.currency.id,
                "provider_id": self.provider.id,
                "reference": self.so_cart.name,
                "operation": "online_redirect",
                "partner_id": self.partner.id,
            }
        )
        self.so_cart.transaction_ids |= transaction
        self.provider.support_manual_capture = True
        transaction._set_authorized()
        self.assertEqual("sale", self.so_cart.typology)
        # The sale order is not confirmed since the transaction amount is wrong
        self.assertEqual("draft", self.so_cart.state)
