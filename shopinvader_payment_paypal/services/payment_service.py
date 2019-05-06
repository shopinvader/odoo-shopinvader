# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class PaymentServicePaypal(Component):
    _inherit = "payment.service.paypal"

    def _validator_add_payment(self):
        return {
            "redirect_success_url": {"type": "string"},
            "redirect_cancel_url": {"type": "string"},
        }

    def _validator_check_payment(self):
        return {"paymentId": {"type": "string"}}

    def _get_connection(self):
        paypal_model_id = self.env.ref(
            "payment_gateway_paypal.account_payment_mode_paypal"
        )
        api, experience_profile = super(
            PaymentServicePaypal, self
        )._get_connection()
        # get payment profile from payment mode info configured on the backend
        transaction = self.collection
        if transaction.origin_id._name == "sale.order":
            backend = self.collection.origin_id.shopinvader_backend_id
            shop_payment = backend.payment_method_ids.filtered(
                lambda a, mode_id=paypal_model_id: a.payment_mode_id == mode_id
            )
            return api, shop_payment.paypal_profile_id or experience_profile
        return api, experience_profile
