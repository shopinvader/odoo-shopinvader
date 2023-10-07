# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from typing import List

from odoo.addons.extendable_fastapi import StrictExtendableBaseModel

from .amount import SaleAmount
from .invoicing import InvoicingInfo
from .sale_order_line import SaleOrderLine
from .shipping import ShippingInfo


class BaseSaleOrder(StrictExtendableBaseModel):
    id: int
    state: str
    name: str
    client_order_ref: str | None = None
    date_order: datetime
    lines: List[SaleOrderLine]
    amount: SaleAmount | None = None
    # TODO discuss about this (should we keep the same schema for this field)
    shipping: ShippingInfo | None = None
    invoicing: InvoicingInfo | None = None
    # TODO END
    typology: str
    note: str | None = None

    @classmethod
    def from_sale_order(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            state=odoo_rec.state,
            name=odoo_rec.name,
            client_order_ref=odoo_rec.name,
            date_order=odoo_rec.date_order,
            lines=[
                SaleOrderLine.from_sale_order_line(line) for line in odoo_rec.order_line
            ],
            amount=SaleAmount.from_sale_order(odoo_rec),
            shipping=ShippingInfo.from_sale_order(odoo_rec),
            invoicing=InvoicingInfo.from_sale_order(odoo_rec),
            note=odoo_rec.note or None,
        )


class SaleOrder(StrictExtendableBaseModel):

    date_delivery: datetime | None = None

    @classmethod
    def from_sale_order(cls, odoo_rec):
        res = super().from_sale_order(odoo_rec)
        res.date_delivery = odoo_rec.date_delivery or None
        return res
