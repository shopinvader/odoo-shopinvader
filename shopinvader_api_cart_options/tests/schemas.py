# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ..schemas import SaleLineOptions as BaseSaleLineOptions


class SaleLineOptions(BaseSaleLineOptions, extends=True):
    engraving: str | None = None
    special: bool = False

    @classmethod
    def from_sale_order_line(cls, odoo_rec):
        rv = super().from_sale_order_line(odoo_rec)
        rv.engraving = odoo_rec.carving or None
        rv.special = odoo_rec.special
        return rv
