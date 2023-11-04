# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from extendable_pydantic import StrictExtendableBaseModel


class CartTransaction(StrictExtendableBaseModel):
    uuid: str | None = None
    qty: float
    product_id: int


class CartSyncInput(StrictExtendableBaseModel):
    transactions: List[CartTransaction]


class ShippingUpdateInfo(StrictExtendableBaseModel):
    address_id: int


class InvoicingUpdateInfo(StrictExtendableBaseModel):
    address_id: int


class CartUpdateInput(StrictExtendableBaseModel):
    client_order_ref: str | None = None
    delivery: ShippingUpdateInfo | None = None
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
            vals["partner_invoicing_id"] = self.invoicing.address_id
        return vals
