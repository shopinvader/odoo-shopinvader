# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from typing import List

from odoo.addons.extendable_fastapi import StrictExtendableBaseModel

from .amount import SaleAmount
from .invoicing import InvoicingInfo
from .sale_order_line import SaleOrderLine
from .shipping import ShippingInfo


class Sale(StrictExtendableBaseModel):
    uuid: str | None = None
    id: int
    state: str
    name: str
    client_order_ref: str | None = None
    date_order: datetime
    date_commitment: datetime | None = None
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
            uuid=odoo_rec.uuid or None,
            id=odoo_rec.id,
            state=odoo_rec.state,
            name=odoo_rec.name,
            typology=odoo_rec.typology,
            client_order_ref=odoo_rec.client_order_ref or None,
            date_order=odoo_rec.date_order,
            date_commitment=odoo_rec.commitment_date or None,
            lines=[
                SaleOrderLine.from_sale_order_line(line) for line in odoo_rec.order_line
            ],
            amount=SaleAmount.from_sale_order(odoo_rec),
            shipping=ShippingInfo.from_sale_order(odoo_rec),
            invoicing=InvoicingInfo.from_sale_order(odoo_rec),
            note=odoo_rec.note or None,
        )


class SaleSearch(StrictExtendableBaseModel):
    name: str | None = None

    def to_odoo_domain(self):
        if self.name:
            return [("name", "ilike", self.name)]
        else:
            return []
