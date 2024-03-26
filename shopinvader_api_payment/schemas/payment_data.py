# Copyright 2024 ACSONE SA (https://acsone.eu).
# @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from pydantic import BaseModel

from .payment_provider import PaymentProvider


class PaymentInput(BaseModel):
    payable: str


class PaymentData(PaymentInput):
    payable_reference: str
    amount: float
    currency_code: str
    amount_formatted: str


class PaymentDataWithMethods(PaymentData):
    providers: list[PaymentProvider]
