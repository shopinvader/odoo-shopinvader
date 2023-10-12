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

    def _convert_delivery_values(self, values):
        if "address_id" in values:
            return {"partner_shipping_id": values["address_id"]}
        else:
            return {}

    def _convert_invoicing_values(self, values):
        if "address_id" in values:
            return {"partner_invoice_id": values["address_id"]}
        else:
            return {}

    def _update_values(self, values):
        if "delivery" in values:
            delivery = values.pop("delivery")
            if delivery:
                values.update(self._convert_delivery_values(delivery))
        if "invoicing" in values:
            invoicing = values.pop("invoicing")
            if invoicing:
                values.update(self._convert_invoicing_values(invoicing))

    def to_vals(self):
        values = self.model_dump(exclude_unset=True)
        self._update_values(values)
        return values
