# Copyright 2023 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import date
from enum import Enum
from typing import Annotated

from extendable_pydantic import StrictExtendableBaseModel
from pydantic import Field

from odoo import api

from .amount import InvoiceAmount


class InvoiceState(str, Enum):
    draft = "draft"
    posted = "posted"
    cancel = "cancel"


class InvoicePaymentState(str, Enum):
    not_paid = "not_paid"
    in_payment = "in_payment"
    paid = "paid"
    partial = "partial"
    reversed = "reversed"
    invoicing_legacy = "invoicing_legacy"


class Invoice(StrictExtendableBaseModel):
    id: int
    name: str
    date_invoice: date
    date_due: date | None = None
    state: InvoiceState
    payment_state: InvoicePaymentState
    ref: str
    payment_reference: str
    amount: InvoiceAmount

    @classmethod
    def from_account_move(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            name=odoo_rec.name or "",
            date_invoice=odoo_rec.invoice_date,
            date_due=odoo_rec.invoice_date_due or None,
            state=InvoiceState(odoo_rec.state),
            payment_state=InvoicePaymentState(odoo_rec.payment_state),
            ref=odoo_rec.ref or "",
            payment_reference=odoo_rec.payment_reference or "",
            amount=InvoiceAmount.from_account_move(odoo_rec),
        )

    @classmethod
    def from_account_moves(cls, odoo_recs):
        return [cls.from_account_move(rec) for rec in odoo_recs]


class InvoiceSearch(StrictExtendableBaseModel, extra="ignore"):
    name: Annotated[
        str | None,
        Field(
            description="When used, the search look for any invoice where name "
            "contains the given value case insensitively."
        ),
    ] = None

    def to_odoo_domain(self, env: api.Environment):
        if self.name:
            return [("name", "ilike", self.name)]
        else:
            return []
