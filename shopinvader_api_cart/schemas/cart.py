# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from typing import List

from odoo.addons.extendable_fastapi import StrictExtendableBaseModel
from odoo.addons.shopinvader_schema_address.schemas import (
    BillingAddress,
    ShippingAddress,
)

from .amount import SaleAmount
from .sale_order_line import SaleOrderLine


class CartTransaction(StrictExtendableBaseModel):
    uuid: str | None = None
    qty: float
    product_id: int


class CartSyncInput(StrictExtendableBaseModel):
    transactions: List[CartTransaction]


class CartResponse(StrictExtendableBaseModel):
    uuid: str | None = None
    id: int
    state: str
    name: str
    date_order: datetime
    lines: List[SaleOrderLine]
    amount: SaleAmount | None = None
    delivery: ShippingAddress | None = None
    invoicing: BillingAddress | None = None
    note: str | None = None

    @classmethod
    def from_cart(cls, odoo_rec):
        return cls.model_construct(
            uuid=odoo_rec.uuid or None,
            id=odoo_rec.id,
            state=odoo_rec.state,
            name=odoo_rec.name,
            date_order=odoo_rec.date_order,
            lines=[
                SaleOrderLine.from_sale_order_line(line) for line in odoo_rec.order_line
            ],
            amount=SaleAmount.from_sale_order(odoo_rec),
            delivery=(
                ShippingAddress.from_res_partner(odoo_rec.partner_shipping_id)
                if odoo_rec.partner_shipping_id
                else None
            ),
            invoicing=(
                BillingAddress.from_res_partner(odoo_rec.partner_invoice_id)
                if odoo_rec.partner_invoice_id
                else None
            ),
            note=odoo_rec.note or None,
        )
