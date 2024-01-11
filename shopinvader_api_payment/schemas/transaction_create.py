# Copyright 2024 ACSONE SA (https://acsone.eu).
# @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Annotated, Literal

from pydantic import Field

from .payment_data import PaymentData


class TransactionCreate(PaymentData):
    flow: Literal["redirect"]  # future: redirect|token
    provider_id: int
    # payment_token_id: int (future)

    # A URL in the frontend where the user will be redirected to after
    # the trip to the payment provider. The following query parameter will be
    # added to the URL: status (success|cancelled|unknown|error)
    # and reference (the transaction reference)
    frontend_redirect_url: Annotated[
        str,
        Field(
            description="A URL in the frontend where the user will be "
            "redirected to after the trip to the payment provider. "
            "The following query parameters will be added to the URL: "
            "status (success|cancelled|pending|unknown|error) and "
            "reference (the transaction reference"
        ),
    ]
