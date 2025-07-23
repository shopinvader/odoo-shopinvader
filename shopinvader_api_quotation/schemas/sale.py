# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.shopinvader_schema_sale.schemas.sale import Sale


class Sale(Sale, extends=True):
    shop_only_quotation: bool | None = None

    @classmethod
    def from_sale_order(cls, odoo_rec):
        res = super().from_sale_order(odoo_rec)
        res.shop_only_quotation = odoo_rec.shop_only_quotation
        return res
