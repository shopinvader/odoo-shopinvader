# Copyright Odoo SA (https://odoo.com)
# Copyright 2024 ACSONE SA (https://acsone.eu).
# @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import hmac
import json
import logging
import pprint
from typing import Annotated
from urllib.parse import quote_plus

from fastapi import Depends, Request
from fastapi.responses import RedirectResponse

from odoo import api, models
from odoo.exceptions import ValidationError

from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.shopinvader_api_payment.routers import payment_router
from odoo.addons.shopinvader_api_payment.routers.utils import (
    add_query_params_in_url,
    tx_state_to_redirect_status,
)

_logger = logging.getLogger(__name__)


@payment_router.post("/payment/providers/sips/return")
async def sips_return(
    request: Request,
    odoo_env: Annotated[api.Environment, Depends(odoo_env)],
):
    """Handle SIPS return.

    After the payment, the user is redirected with a POST to this endpoint. We handle
    the notification data to update the transaction status. We then redirect the browser
    with a GET to the frontend_return_url, with the transaction reference as parameter.

    Future: we could also return a unguessable transaction uuid that the front could the
    use to consult /payment/transactions/{uuid} and obtain the transaction status.
    """
    data = await request.form()
    _logger.info(
        "return notification received from SIPS with data:\n%s", pprint.pformat(data)
    )
    # Check the integrity of the notification
    tx_sudo = (
        odoo_env["payment.transaction"]
        .sudo()
        ._get_tx_from_notification_data(
            "sips",
            data,
        )
    )
    try:
        odoo_env[
            "shopinvader_provider_sips.payment_sips_router.helper"
        ]._verify_sips_signature(tx_sudo, data)
    except Exception:
        return {"error": "Invalid sips signature"}

    notification_data = tx_sudo._sips_notification_data_to_object(data.get("Data"))
    returnContext = json.loads(notification_data.get("returnContext", "{}"))
    reference = returnContext.get("reference")
    frontend_redirect_url = returnContext.get("frontend_redirect_url")

    try:
        tx_sudo._handle_notification_data("sips", data)
        status = tx_state_to_redirect_status(tx_sudo.state)
    except Exception:
        _logger.exception("unable to handle sips notification data", exc_info=True)
        status = "error"
    return RedirectResponse(
        url=add_query_params_in_url(
            frontend_redirect_url,
            {"status": status, "reference": quote_plus(reference)},
        ),
        status_code=303,
    )


@payment_router.post("/payment/providers/sips/webhook")
async def sips_webhook(
    request: Request,
    odoo_env: Annotated[api.Environment, Depends(odoo_env)],
):
    """Handle SIPS webhook."""
    data = await request.form()
    _logger.info(
        "webhook notification received from SIPS with data:\n%s", pprint.pformat(data)
    )
    try:
        tx_sudo = (
            odoo_env["payment.transaction"]
            .sudo()
            ._get_tx_from_notification_data(
                "sips",
                data,
            )
        )
        odoo_env[
            "shopinvader_api_payment_provider_sips.payment_sips_router.helper"
        ]._verify_sips_signature(tx_sudo, data)
        tx_sudo._handle_notification_data("sips", data)
    except Exception:
        _logger.exception("unable to handle sips notification data", exc_info=True)
    return ""


class ShopinvaderApiPaymentProviderSipsRouterHelper(models.AbstractModel):
    _name = "shopinvader_provider_sips.payment_sips_router.helper"
    _description = "ShopInvader API Payment Provider Sips Router Helper"

    def _verify_sips_signature(self, tx_sudo, data):
        """Verify the SIPS signature."""
        expected_signature = tx_sudo.provider_id._sips_generate_shasign(
            data.get("Data")
        )
        if not expected_signature:
            _logger.warning("received sips notification without signature")
            raise ValidationError()
        if not hmac.compare_digest(data.get("Seal", ""), expected_signature):
            _logger.warning("received sips notification with invalid signature")
            raise ValidationError()
