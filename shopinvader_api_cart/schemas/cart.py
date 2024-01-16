# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List
from uuid import UUID

from extendable_pydantic import StrictExtendableBaseModel


class CartTransaction(StrictExtendableBaseModel):
    uuid: UUID | None = None
    qty: float
    product_id: int


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
