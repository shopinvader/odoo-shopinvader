# Copyright 2024 ACSONE SA (https://acsone.eu).
# @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Annotated

from pydantic import Field

from odoo.addons.shopinvader_api_payment.schemas import (
    TransactionProcessingValues as BaseTransactionProcessingValues,
)


class TransactionProcessingValues(BaseTransactionProcessingValues, extends=True):
    session_id: Annotated[
        str | None,
        Field(description="Stripe session id, for redirect or validation mode"),
    ] = None
    publishable_key: Annotated[
        str | None,
        Field(description="Stripe publishable key, for redirect or validation mode"),
    ] = None
    client_secret: Annotated[
        str | None,
        Field(description="Stripe client secret, for express checkout mode"),
    ] = None
