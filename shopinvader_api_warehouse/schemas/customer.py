# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_api_customer.schemas.customer import (
    Customer as BaseCustomer,
)
from odoo.addons.shopinvader_api_customer.schemas.customer import (
    CustomerUpdate as BaseCustomerUpdate,
)

from .warehouse import Warehouse


class Customer(BaseCustomer, extends=True):
    default_warehouse: Warehouse | None = None

    @classmethod
    def from_res_partner(cls, odoo_rec):
        res = super().from_res_partner(odoo_rec)
        res.default_warehouse = (
            Warehouse.from_stock_warehouse(
                odoo_rec.shopinvader_default_warehouse_id, partner=odoo_rec
            )
            if odoo_rec.shopinvader_default_warehouse_id
            else None
        )
        return res


class CustomerUpdate(BaseCustomerUpdate, extends=True):
    default_warehouse_id: int | None = None

    def to_res_partner_vals(self) -> dict:
        vals = super().to_res_partner_vals()
        if self.default_warehouse_id is not None:
            vals["shopinvader_default_warehouse_id"] = self.default_warehouse_id
        return vals
