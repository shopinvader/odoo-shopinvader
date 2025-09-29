# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_schema_sale.schemas import SaleLine as BaseSaleLine


class SaleLine(BaseSaleLine, extends=True):
    is_reward_line: bool

    @classmethod
    def from_sale_order_line(cls, odoo_rec):
        obj = super().from_sale_order_line(odoo_rec)
        obj.is_reward_line = odoo_rec.is_reward_line
        return obj

    @classmethod
    def _get_sale_line_type(cls, odoo_rec) -> str:
        if odoo_rec.is_reward_line:
            return "reward"
        return super()._get_sale_line_type(odoo_rec)
