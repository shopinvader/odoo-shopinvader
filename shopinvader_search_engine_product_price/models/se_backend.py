# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SeBackend(models.Model):

    _inherit = "se.backend"

    @api.model
    def _default_pricelist_id(self):
        return self.env.ref("product.list0")

    pricelist_id = fields.Many2one(
        "product.pricelist",
        string="Pricelist",
        default=lambda self: self._default_pricelist_id(),
    )
