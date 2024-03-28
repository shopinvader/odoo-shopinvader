# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List, Optional

from extendable_pydantic import StrictExtendableBaseModel

from odoo.addons.shopinvader_schema_sale.schemas import Sale as BaseSale


class CartStep(StrictExtendableBaseModel):
    code: str
    name: str

    @classmethod
    def from_sale_cart_step(cls, rec):
        return {"name": rec.name, "code": rec.code} if rec else None

    @classmethod
    def from_sale_cart_steps(cls, recs):
        return [cls.from_sale_cart_step(x) for x in recs]


class Sale(BaseSale, extends=True):

    step: Optional[CartStep] = None
    done_steps: Optional[List[CartStep]] = []

    @classmethod
    def from_sale_order(cls, odoo_rec):
        obj = super().from_sale_order(odoo_rec)
        obj.step = CartStep.from_sale_cart_step(odoo_rec.cart_step_id)
        obj.done_steps = CartStep.from_sale_cart_steps(odoo_rec.cart_step_done_ids)
        return obj
