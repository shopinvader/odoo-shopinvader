from typing import Generic, TypeVar

from extendable_pydantic import StrictExtendableBaseModel

from odoo import Command

from odoo.addons.shopinvader_schema_sale.schemas.sale import Sale


class Sale(Sale, extends=True):
    shop_only_quotation: bool | None = None

    @classmethod
    def from_sale_order(cls, odoo_rec):
        res = super().from_sale_order(odoo_rec)
        res.shop_only_quotation = odoo_rec.shop_only_quotation
        return res


class QuotationConfirmInput(StrictExtendableBaseModel):
    """Extend it if you need params for the confirmation"""


class QuotationLineCreateRequest(StrictExtendableBaseModel, extra="ignore"):
    sequence: int | None = None
    product_id: int
    quantity: float


class QuotationCreateRequest(StrictExtendableBaseModel, extra="ignore"):
    name: str
    lines: list[QuotationLineCreateRequest] | None = None
    client_order_ref: str | None = None
    typology: str


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
    lines: list[QuotationUpdateLineRequest] | None = None

    def to_sale_order_vals(self) -> dict:
        return {
            "client_order_ref": self.client_order_ref,
            "order_line": [
                Command.update(
                    line.line_id,
                    {
                        "product_id": line.product_id,
                        "product_uom_qty": line.quantity,
                        "sequence": line.sequence,
                    },
                )
                for line in self.lines
            ],
        }
