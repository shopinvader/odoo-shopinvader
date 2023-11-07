# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from typing import Annotated, List

from pydantic import Field

from odoo import api

from odoo.addons.extendable_fastapi import StrictExtendableBaseModel

from .amount import SaleAmount
from .delivery import DeliveryInfo
from .invoicing import InvoicingInfo
from .sale_line import SaleLine


class Sale(StrictExtendableBaseModel):
    id: int
    state: str
    name: str
    client_order_ref: str | None = None
    date_order: datetime
    date_commitment: datetime | None = None
    lines: List[SaleLine]
    amount: SaleAmount | None = None
    delivery: DeliveryInfo | None = None
    invoicing: InvoicingInfo | None = None
    typology: str
    note: str | None = None

    @classmethod
    def from_sale_order(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            state=odoo_rec.shopinvader_state,
            name=odoo_rec.name,
            typology=odoo_rec.typology,
            client_order_ref=odoo_rec.client_order_ref or None,
            date_order=odoo_rec.date_order,
            date_commitment=odoo_rec.commitment_date or None,
            lines=[SaleLine.from_sale_order_line(line) for line in odoo_rec.order_line],
            amount=SaleAmount.from_sale_order(odoo_rec),
            delivery=DeliveryInfo.from_sale_order(odoo_rec),
            invoicing=InvoicingInfo.from_sale_order(odoo_rec),
            note=odoo_rec.note or None,
        )


class SaleSearch(StrictExtendableBaseModel, extra="ignore"):
    name: Annotated[
        str | None,
        Field(
            description="When used, the search look for any sale oder where name "
            "contains the given value case insensitively."
        ),
    ] = None

    def to_odoo_domain(self, env: api.Environment):
        if self.name:
            return [("name", "ilike", self.name)]
        else:
            return []
