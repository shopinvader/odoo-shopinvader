# Copyright Odoo SA (https://odoo.com)
# Copyright 2024 ACSONE SA (https://acsone.eu).
# @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from urllib.parse import quote_plus, urljoin

from odoo import models

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_stripe.const import PAYMENT_METHOD_TYPES


class PaymentTransactionStripe(models.Model):
    _inherit = "payment.transaction"

    def _stripe_create_checkout_session(self):
        """Create and return a Checkout Session.

        :return: The Checkout Session
        :rtype: dict
        """
        shopinvader_api_payment = self.env.context.get("shopinvader_api_payment")

        if not shopinvader_api_payment:
            return super()._stripe_create_checkout_session()

        shopinvader_api_payment_frontend_redirect_url = self.env.context.get(
            "shopinvader_api_payment_frontend_redirect_url"
        )
        shopinvader_api_payment_base_url = self.env.context.get(
            "shopinvader_api_payment_base_url"
        )

        # !!! code copied from Odoo payment_stripe module, to use different return and
        # !!! webhook urls

        def get_linked_pmts(linked_pms_):
            linked_pmts_ = linked_pms_
            card_pms_ = [
                self.env.ref(
                    f"payment.payment_icon_cc_{pm_code_}", raise_if_not_found=False
                )
                for pm_code_ in ("visa", "mastercard", "american_express", "discover")
            ]
            card_pms_ = [
                pm_ for pm_ in card_pms_ if pm_ is not None
            ]  # Remove deleted card PMs.
            if any(pm_.name.lower() in linked_pms_ for pm_ in card_pms_):
                linked_pmts_ += ["card"]
            return linked_pmts_

        # Filter payment method types by available payment method
        existing_pms = [
            pm.name.lower() for pm in self.env["payment.icon"].search([])
        ] + ["card"]
        linked_pms = [pm.name.lower() for pm in self.provider_id.payment_icon_ids]
        pm_filtered_pmts = filter(
            # If the PM (payment.icon) record related to a PMT doesn't exist,
            # don't filter out the PMT because the user couldn't even
            # have linked it to the provider in the first place.
            lambda pmt: pmt.name in get_linked_pmts(linked_pms)
            or pmt.name not in existing_pms,
            PAYMENT_METHOD_TYPES,
        )
        # Filter payment method types by country code
        country_code = self.partner_country_id and self.partner_country_id.code.lower()
        country_filtered_pmts = filter(
            lambda pmt: not pmt.countries or country_code in pmt.countries,
            pm_filtered_pmts,
        )
        # Filter payment method types by currency name
        currency_name = self.currency_id.name.lower()
        currency_filtered_pmts = filter(
            lambda pmt: not pmt.currencies or currency_name in pmt.currencies,
            country_filtered_pmts,
        )
        # Filter payment method types by recurrence if the transaction must be tokenized
        if self.tokenize:
            recurrence_filtered_pmts = filter(
                lambda pmt: pmt.recurrence == "recurring", currency_filtered_pmts
            )
        else:
            recurrence_filtered_pmts = currency_filtered_pmts
        # Build the session values related to payment method types
        pmt_values = {}
        for pmt_id, pmt_name in enumerate(
            map(lambda pmt: pmt.name, recurrence_filtered_pmts)
        ):
            pmt_values[f"payment_method_types[{pmt_id}]"] = pmt_name

        # Create the session according to the operation and return it
        customer = self._stripe_create_customer()
        common_session_values = self._get_common_stripe_session_values(
            pmt_values, customer
        )
        self.provider_id.get_base_url()
        if self.operation == "online_redirect":
            return_url = (
                f'{urljoin(shopinvader_api_payment_base_url, "stripe/checkout_return")}'
                f"?reference={quote_plus(self.reference)}"
                f"&redirect_url={quote_plus(shopinvader_api_payment_frontend_redirect_url)}"
            )
            # Specify a future usage for the payment intent to:
            # 1. attach the payment method to the created customer
            # 2. trigger a 3DS check if one if required, while the customer is still present
            future_usage = "off_session" if self.tokenize else None
            capture_method = (
                "manual" if self.provider_id.capture_manually else "automatic"
            )
            amount_to_minor_currency = payment_utils.to_minor_currency_units(
                self.amount, self.currency_id
            )
            checkout_session = self.provider_id._stripe_make_request(
                "checkout/sessions",
                payload={
                    **common_session_values,
                    "mode": "payment",
                    "success_url": return_url,
                    "cancel_url": return_url,
                    "line_items[0][price_data][currency]": self.currency_id.name,
                    "line_items[0][price_data][product_data][name]": self.reference,
                    "line_items[0][price_data][unit_amount]": amount_to_minor_currency,
                    "line_items[0][quantity]": 1,
                    "payment_intent_data[description]": self.reference,
                    "payment_intent_data[setup_future_usage]": future_usage,
                    "payment_intent_data[capture_method]": capture_method,
                },
            )
            self.stripe_payment_intent = checkout_session["payment_intent"]
        else:  # 'validation'
            raise NotImplementedError  # TODO: in the future
            # {CHECKOUT_SESSION_ID} is a template filled by Stripe when the Session is created
            # return_url = (
            #     f"{urls.url_join(base_url, StripeController._validation_return_url)}"
            #     f"?reference={urls.url_quote_plus(self.reference)}"
            #     f"&checkout_session_id={{CHECKOUT_SESSION_ID}}"
            # )
            # checkout_session = self.provider_id._stripe_make_request(
            #     "checkout/sessions",
            #     payload={
            #         **common_session_values,
            #         "mode": "setup",
            #         "success_url": return_url,
            #         "cancel_url": return_url,
            #         "setup_intent_data[description]": self.reference,
            #     },
            # )
        return checkout_session
