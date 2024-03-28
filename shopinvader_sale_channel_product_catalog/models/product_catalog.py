# Copyright 2023 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductCatalog(models.Model):
    _inherit = "product.catalog"

    shopinvader_backend_ids = fields.Many2many(
        comodel_name="shopinvader.backend",
        compute="_compute_shopinvader_backend_ids",
        readonly=True,
    )

    def _compute_shopinvader_backend_ids(self):
        for rec in self:
            rec.shopinvader_backend_ids = rec.mapped("channel_ids").mapped(
                "shopinvader_backend_ids"
            )
