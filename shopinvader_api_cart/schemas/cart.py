# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from typing import List, Optional

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.pydantic import utils
from odoo.addons.shopinvader_schema_address.schemas import (
    BillingAddress,
    ShippingAddress,
)

from .amount import SaleAmount
from .sale_order_line import SaleOrderLine


class CartTransaction(BaseModel, metaclass=ExtendableModelMeta):
    uuid: Optional[str]
    qty: float
    product_id: int

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter


class CartSyncInput(BaseModel, metaclass=ExtendableModelMeta):
    transactions: List[CartTransaction]


class CartResponse(BaseModel, metaclass=ExtendableModelMeta):
    uuid: Optional[str]
    id: int
    state: str
    name: str
    date_order: datetime
    lines: List[SaleOrderLine]
    amount: Optional[SaleAmount]
    delivery: Optional[ShippingAddress]
    invoicing: Optional[BillingAddress]
    note: Optional[str]

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter

    @classmethod
    def from_cart(cls, odoo_rec):
        res = cls.construct()
        res.uuid = odoo_rec.uuid or None
        res.id = odoo_rec.id
        res.state = odoo_rec.state
        res.name = odoo_rec.name
        res.date_order = odoo_rec.date_order
        res.lines = [
            SaleOrderLine.from_sale_order_line(line) for line in odoo_rec.order_line
        ]
        res.amount = SaleAmount.from_sale_order(odoo_rec)
        res.delivery = (
            ShippingAddress.from_res_partner(odoo_rec.partner_shipping_id)
            if odoo_rec.partner_shipping_id
            else None
        )
        res.invoicing = (
            BillingAddress.from_res_partner(odoo_rec.partner_invoice_id)
            if odoo_rec.partner_invoice_id
            else None
        )
        res.note = odoo_rec.note or None

        return res
