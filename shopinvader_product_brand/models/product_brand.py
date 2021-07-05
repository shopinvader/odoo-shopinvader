# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductBrand(models.Model):
    _inherit = "product.brand"

    shopinvader_bind_ids = fields.One2many(
        "shopinvader.brand",
        "record_id",
        string="Shopinvader Binding",
        context={"active_test": False},
    )
    active = fields.Boolean(default=True, inverse="_inverse_active")

    def _inverse_active(self):
        brands = self.filtered(lambda p: not p.active)
        brands.mapped("shopinvader_bind_ids").write({"active": False})
