# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel

from .amount import SaleLineAmount


class SaleOrderLine(StrictExtendableBaseModel):
    id: int
    product_id: int
    name: str
    amount: SaleLineAmount | None = None
    qty: float

    @classmethod
    def from_sale_order_line(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            product_id=odoo_rec.product_id.id,
            name=odoo_rec.name,
            amount=SaleLineAmount.from_sale_order_line(odoo_rec),
            qty=odoo_rec.product_uom_qty,
        )
