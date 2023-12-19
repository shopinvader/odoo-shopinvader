# Copyright 2024 ACSONE SA (https://acsone.eu).
# @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Literal

from pydantic import BaseModel


class TransactionProcessingValues(BaseModel):
    flow: Literal["redirect"]
    provider_id: int
    provider_code: str
    reference: str  # transaction reference
    amount: float
    currency_id: int
    partner_id: int
    redirect_form_html: str | None = None
