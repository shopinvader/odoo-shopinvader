# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_schema_address.schemas import (
    InvoicingAddress as BaseInvoicingAddress,
)


class InvoicingAddress(BaseInvoicingAddress, extends=True):
    sale_profile: str | None = None

    @classmethod
    def from_res_partner(cls, odoo_rec):
        res = super().from_res_partner(odoo_rec)
        res.sale_profile = odoo_rec.sale_profile_id.code or None
        return res
