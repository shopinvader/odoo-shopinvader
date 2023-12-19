# Copyright 2024 ACSONE SA (https://acsone.eu).
# @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from pydantic import BaseModel

from .payment_provider import PaymentProvider


class PaymentData(BaseModel):
    payable: str
    payable_reference: str
    amount: float
    currency_id: int
    partner_id: int
    company_id: int
    access_token: str


class PaymentDataWithProviders(PaymentData):
    providers: list[PaymentProvider]
