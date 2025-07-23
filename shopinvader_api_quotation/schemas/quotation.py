# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from enum import Enum
from typing import Annotated, Generic, TypeVar

from extendable_pydantic import StrictExtendableBaseModel
from pydantic import Field

from odoo.addons.shopinvader_schema_sale.schemas.sale import SaleSearch


class QuotationState(Enum):
    cancel = "cancel"
    draft = "draft"
    customer_request = "customer_request"
    waiting_acceptation = "waiting_acceptation"
    accepted = "accepted"


class QuotationSearch(SaleSearch):
    """Extend it if you need specific params for searching quotations"""

    client_order_ref: Annotated[
        str | None,
        Field(
            description="When used, the search look for any quotation oder "
            "where client_order_ref contains the given value case insensitively."
        ),
    ] = None
    quotation_state: QuotationState | None = None

    def to_odoo_domain(self, env):
        domain = super().to_odoo_domain(env)
        if self.client_order_ref:
            domain.append(("client_order_ref", "ilike", self.client_order_ref))
        if self.quotation_state:
            domain.append(("quotation_state", "=", self.quotation_state.value))
        return domain


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
