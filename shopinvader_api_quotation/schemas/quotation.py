# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from typing import Generic, TypeVar

from extendable_pydantic import StrictExtendableBaseModel


class QuotationConfirmInput(StrictExtendableBaseModel):
    """Extend it if you need params for the confirmation"""


class QuotationLineCreateRequest(StrictExtendableBaseModel, extra="ignore"):
    sequence: int | None = None
    product_id: int
    quantity: float


class QuotationCreateRequest(StrictExtendableBaseModel, extra="ignore"):
    lines: list[QuotationLineCreateRequest] | None = None
    client_order_ref: str | None = None


class QuotationAddLineRequest(StrictExtendableBaseModel, extra="ignore"):
    sequence: int | None = None
    product_id: int
    quantity: float


class QuotationUpdateLineRequest(StrictExtendableBaseModel, extra="ignore"):
    line_id: int
    sequence: int | None = None
    product_id: int
    quantity: float


class QuotationDeleteLineRequest(StrictExtendableBaseModel, extra="ignore"):
    line_id: int


T = TypeVar("T")


class QuotationLines(StrictExtendableBaseModel, Generic[T]):
    lines: list[T] = []


class QuotationUpdateInput(StrictExtendableBaseModel, extra="ignore"):
    client_order_ref: str | None = None
    lines: list[QuotationUpdateLineRequest | QuotationAddLineRequest] | None = None
