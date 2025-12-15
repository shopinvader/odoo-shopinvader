# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_schema_sale.schemas import sale

from .warehouse import Warehouse


class Sale(sale.Sale, extends=True):
    warehouse: Warehouse | None = None

    @classmethod
    def from_sale_order(cls, odoo_rec):
        res = super().from_sale_order(odoo_rec)
        res.warehouse = (
            Warehouse.from_stock_warehouse(odoo_rec.warehouse_id)
            if odoo_rec.warehouse_id
            else None
        )
        return res
