# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_schema_sale.schemas import sale


class Sale(sale.Sale, extends=True):
    @classmethod
    def from_sale_order(cls, odoo_rec):
        res = super().from_sale_order(odoo_rec)
        res.state = odoo_rec.shopinvader_state
        return res
