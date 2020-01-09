# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductSetAdd(models.TransientModel):
    _inherit = "product.set.add"

    shopinvader_backend_id = fields.Many2one(
        related="product_set_id.shopinvader_backend_id"
    )

    def _get_lines(self):
        lines = super()._get_lines()
        if self.shopinvader_backend_id:
            # consider only product lines that are allowed
            # for current backend and partner
            for line in lines:
                if line.product_id._add_to_cart_allowed(
                    self.shopinvader_backend_id, partner=self.partner_id
                ):
                    yield line
