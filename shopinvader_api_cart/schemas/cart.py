# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from extendable_pydantic import StrictExtendableBaseModel
from odoo.addons.shopinvader_schema_sale.schemas import BaseSale


class CartTransaction(StrictExtendableBaseModel):
    uuid: str | None = None
    qty: float
    product_id: int


class CartSyncInput(StrictExtendableBaseModel):
    transactions: List[CartTransaction]


class CartResponse(BaseSale):
    uuid: str | None = None

    @classmethod
    def from_sale_order(cls, odoo_rec):
        res = super().from_sale_order(odoo_rec)
        res.uuid = odoo_rec.uuid or None
        return res
