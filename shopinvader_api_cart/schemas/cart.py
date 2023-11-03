# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from extendable_pydantic import StrictExtendableBaseModel


class CartTransactionOption(StrictExtendableBaseModel):
    """Optionnal information for transaction"""

    @classmethod
    def _prepare_from_sale_line(cls, line):
        return {}

    @classmethod
    def from_sale_line(cls, line):
        return cls.model_validate(cls._prepare_from_line(line))


class CartTransaction(StrictExtendableBaseModel):
    uuid: str | None = None
    qty: float
    product_id: int
    options: CartTransactionOption | None = None


class CartSyncInput(StrictExtendableBaseModel, extra="ignore"):
    transactions: List[CartTransaction]


class DeliveryUpdateInfo(StrictExtendableBaseModel, extra="ignore"):
    address_id: int


class InvoicingUpdateInfo(StrictExtendableBaseModel, extra="ignore"):
    address_id: int


class CartUpdateInput(StrictExtendableBaseModel, extra="ignore"):
    client_order_ref: str | None = None
    delivery: DeliveryUpdateInfo | None = None
    invoicing: InvoicingUpdateInfo | None = None
    note: str | None = None

    def convert_to_sale_write(self):
        vals = {}
        data = self.model_dump(exclude_unset=True)
        if "client_order_ref" in data:
            vals["client_order_ref"] = self.client_order_ref
        if "note" in data:
            vals["note"] = self.note
        if (data.get("delivery") or {}).get("address_id"):
            vals["partner_shipping_id"] = self.delivery.address_id
        if (data.get("invoicing") or {}).get("address_id"):
            vals["partner_invoice_id"] = self.invoicing.address_id
        return vals
