# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel

from odoo.tools.float_utils import json_float_round

from .amount import SaleLineAmount


class SaleLine(StrictExtendableBaseModel):
    id: int
    product_id: int
    name: str
    amount: SaleLineAmount | None = None
    qty: float
    type: str

    @classmethod
    def from_sale_order_line(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            product_id=odoo_rec.product_id.id,
            name=odoo_rec.name,
            amount=SaleLineAmount.from_sale_order_line(odoo_rec),
            qty=json_float_round(
                odoo_rec.product_uom_qty,
                precision_digits=len(str(odoo_rec.product_uom.rounding).split(".")[1]),
            ),
            type=cls._get_sale_line_type(odoo_rec),
        )

    @classmethod
    def _get_sale_line_type(cls, odoo_rec) -> str:
        if odoo_rec.display_type == "line_section":
            return "section"
        if odoo_rec.display_type == "line_note":
            return "note"
        return "product"
