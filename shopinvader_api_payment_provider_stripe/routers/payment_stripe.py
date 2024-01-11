# Copyright Odoo SA (https://odoo.com)
# Copyright 2024 ACSONE SA (https://acsone.eu).
# @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
import pprint
from typing import Annotated
from urllib.parse import quote_plus

from fastapi import Depends, Request
from fastapi.responses import RedirectResponse

from odoo import api

from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.payment_stripe.controllers.main import (
    StripeController as OdooStripeController,
)
from odoo.addons.shopinvader_api_payment.routers import payment_router
from odoo.addons.shopinvader_api_payment.routers.utils import (
    add_query_params_in_url,
    tx_state_to_redirect_status,
)

_logger = logging.getLogger(__name__)


@payment_router.get("/payment/providers/stripe/checkout_return")
def stripe_return_from_checkout(
    request: Request,
    odoo_env: Annotated[api.Environment, Depends(odoo_env)],
):
    """Process the notification data sent by Stripe after redirection from checkout.

    From Odoo payment_stripe /payment/stripe/checkout_return route.
    """
    # convert QueryParam to dict so it is mutable, because
    # _include_payment_intent_in_notification_data wants to mutate it.
    data = dict(request.query_params)

    # Retrieve the tx based on the tx reference included in the return url
    tx_sudo = (
        odoo_env["payment.transaction"]
        .sudo()
        ._get_tx_from_notification_data("stripe", data)
    )

    # Fetch the PaymentIntent, Charge and PaymentMethod objects from Stripe
    payment_intent = tx_sudo.provider_id._stripe_make_request(
        f"payment_intents/{tx_sudo.stripe_payment_intent}", method="GET"
    )
    _logger.info(
        "received payment_intents response:\n%s", pprint.pformat(payment_intent)
    )
    OdooStripeController._include_payment_intent_in_notification_data(
        payment_intent, data
    )

    # Handle the notification data crafted with Stripe API objects
    tx_sudo._handle_notification_data("stripe", data)

    # Redirect the user to the status page
    status = tx_state_to_redirect_status(tx_sudo.state)
    tx_reference = data.get("reference", "")
    redirect_url = data.get("redirect_url", "")
    return RedirectResponse(
        url=add_query_params_in_url(
            redirect_url, {"status": status, "reference": quote_plus(tx_reference)}
        ),
        status_code=303,
    )
