# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.pydantic import utils

from .amount import SaleLineAmount


class SaleOrderLine(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    product_id: int
    name: str
    amount: SaleLineAmount | None
    qty: float

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter

    @classmethod
    def from_orm(cls, odoo_rec):
        res = cls.construct()
        res.id = odoo_rec.id
        res.product_id = odoo_rec.product_id
        res.name = odoo_rec.name
        res.amount = SaleLineAmount.from_orm(odoo_rec)
        res.qty = odoo_rec.product_uom_qty

        return res
