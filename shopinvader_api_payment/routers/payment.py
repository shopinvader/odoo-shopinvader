# Copyright Odoo SA (https://odoo.com)
# Copyright 2024 ACSONE SA (https://acsone.eu).
# @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
import logging
from typing import Annotated
from urllib.parse import urljoin

from fastapi import APIRouter, Depends, HTTPException, Request

from odoo import api, models

from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment.models.payment_provider import PaymentProvider

from ..schemas import (
    PaymentDataWithMethods,
    PaymentProvider as PaymentProviderSchema,
    TransactionCreate,
    TransactionProcessingValues,
)
from .utils import Payable

_logger = logging.getLogger(__name__)

payment_router = APIRouter(tags=["payment"])


@payment_router.get("/payment/methods")
def pay(
    payable: str,
    access_token: str,
    odoo_env: Annotated[api.Environment, Depends(odoo_env)],
):
    """Available payment providers.

    This route is public, so it is possible to pay anonymously provided that the
    parameters are obtained securely by another mean. An authenticated use can
    obtain the parameters with the /payment/payable route.
    """
    if not payment_utils.check_access_token(
        access_token,
        payable,
    ):
        _logger.info("Invalid access token")
        raise HTTPException(403)
    payable_obj = Payable.model_validate(json.loads(payable))
    # This method is similar to Odoo's PaymentPortal.payment_pay
    providers_sudo = (
        odoo_env["payment.provider"]
        .sudo()
        ._get_compatible_providers(
            payable_obj.company_id,
            payable_obj.partner_id,
            payable_obj.amount,
            currency_id=payable_obj.currency_id,
        )
    )
    return PaymentDataWithMethods(
        payable=payable,
        payable_reference=payable_obj.payable_reference,
        amount=payable_obj.amount,
        currency_code=odoo_env["res.currency"].browse(payable_obj.currency_id).name,
        access_token=access_token,
        providers=[
            PaymentProviderSchema.from_payment_provider(provider)
            for provider in providers_sudo
        ],
    )


@payment_router.post("/payment/transactions")
def transaction(
    data: TransactionCreate,
    request: Request,
    odoo_env: Annotated[api.Environment, Depends(odoo_env)],
) -> TransactionProcessingValues:
    """Create a payment transaction.

    Input is data obtained from /payment/providers, with the provider selected by the
    user. This route is public, so it is possible to pay anonymously.
    """
    if not payment_utils.check_access_token(
        data.access_token,
        data.payable,
    ):
        _logger.info("Invalid access token")
        raise HTTPException(403)
    payable_obj = Payable.model_validate(json.loads(data.payable))
    # similar to Odoo's /payment/transaction route
    if data.flow == "redirect":
        providers_sudo = (
            odoo_env["payment.provider"]
            .sudo()
            ._get_compatible_providers(
                payable_obj.company_id,
                payable_obj.partner_id,
                payable_obj.amount,
                currency_id=payable_obj.currency_id,
            )
        )
        if not data.provider_id or data.provider_id not in providers_sudo.ids:
            _logger.info(
                "Invalid provider %s for partner %s",
                data.provider_id,
                payable_obj.partner_id,
            )
            raise HTTPException(403)
        provider_sudo = odoo_env["payment.provider"].sudo().browse(data.provider_id)

        # Create the transaction
        transaction_values = odoo_env[
            "shopinvader_api_payment.payment_router.helper"
        ]._get_tx_create_values(data, provider_sudo, odoo_env)
        tx_sudo = (
            odoo_env["payment.transaction"]
            .sudo()
            .with_context(
                shopinvader_api_payment=True,
                shopinvader_api_payment_frontend_redirect_url=data.frontend_redirect_url,
                shopinvader_api_payment_base_url=urljoin(
                    str(request.url), "providers/"
                ),
            )
            .create(transaction_values)
        )
        tx_sudo._log_sent_message()
        return TransactionProcessingValues(
            flow="redirect", **tx_sudo._get_processing_values()
        )
    else:
        raise NotImplementedError("Only redirect flow is supported")


class ShopinvaderApiPaymentRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_payment.payment_router.helper"
    _description = "ShopInvader API Payment Router Helper"

    def _get_additional_transaction_create_values(
        self, data: TransactionCreate
    ) -> dict:
        # Intended to be extended for invoices, carts...
        additional_transaction_create_values = {}
        return additional_transaction_create_values

    def _get_tx_create_values(
        self,
        data: TransactionCreate,
        provider_sudo: PaymentProvider,
        odoo_env: Annotated[api.Environment, Depends(odoo_env)],
    ) -> dict:
        payable_obj = Payable.model_validate(json.loads(data.payable))
        additional_transaction_create_values = (
            self._get_additional_transaction_create_values(data)
        )

        is_validation = False  # future
        # compute transaction reference from payable reference
        tx_reference = (
            odoo_env["payment.transaction"]
            .sudo()
            ._compute_reference(
                provider_code=provider_sudo.code,
                prefix=payable_obj.payable_reference,
                # TODO are custom_create_values and kwargs really needed
                # **(custom_create_values or {}),
                # **kwargs
            )
        )

        return {
            "provider_id": data.provider_id,
            "reference": tx_reference,
            "amount": payable_obj.amount,
            "currency_id": payable_obj.currency_id,
            "partner_id": payable_obj.partner_id,
            # 'token_id': token_id,
            "operation": f"online_{data.flow}" if not is_validation else "validation",
            "tokenize": False,
            **additional_transaction_create_values,
        }
