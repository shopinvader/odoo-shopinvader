# Copyright Odoo SA (https://odoo.com)
# Copyright 2024 ACSONE SA (https://acsone.eu).
# @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
from urllib.parse import urljoin

from odoo import models

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_sips.models.const import SUPPORTED_CURRENCIES


class PaymentTransactionSips(models.Model):
    _inherit = "payment.transaction"

    def _get_specific_rendering_values(self, processing_values):
        """Override of payment to return Sips-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific
        processing values of the transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """
        shopinvader_api_payment = self.env.context.get("shopinvader_api_payment")

        if self.provider_code != "sips" or not shopinvader_api_payment:
            return super()._get_specific_rendering_values(processing_values)

        shopinvader_api_payment_frontend_redirect_url = self.env.context.get(
            "shopinvader_api_payment_frontend_redirect_url"
        )
        shopinvader_api_payment_base_url = self.env.context.get(
            "shopinvader_api_payment_base_url"
        )

        # !!! code copied from Odoo payment_sips module, to use different return and
        # !!! webhook urls

        data = {
            "amount": payment_utils.to_minor_currency_units(
                self.amount, self.currency_id
            ),
            "currencyCode": SUPPORTED_CURRENCIES[
                self.currency_id.name
            ],  # The ISO 4217 code
            "merchantId": self.provider_id.sips_merchant_id,
            "normalReturnUrl": urljoin(shopinvader_api_payment_base_url, "sips/return"),
            "automaticResponseUrl": urljoin(
                shopinvader_api_payment_base_url, "sips/webhook"
            ),
            "transactionReference": self.reference,
            "statementReference": self.reference,
            "keyVersion": self.provider_id.sips_key_version,
            "returnContext": json.dumps(
                dict(
                    reference=self.reference,
                    frontend_redirect_url=shopinvader_api_payment_frontend_redirect_url,
                )
            ),
        }
        api_url = (
            self.provider_id.sips_prod_url
            if self.provider_id.state == "enabled"
            else self.provider_id.sips_test_url
        )
        data = "|".join([f"{k}={v}" for k, v in data.items()])
        return {
            "api_url": api_url,
            "Data": data,
            "InterfaceVersion": self.provider_id.sips_version,
            "Seal": self.provider_id._sips_generate_shasign(data),
        }
