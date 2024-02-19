# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SeIndex(models.Model):

    _inherit = "se.index"

    pricelist_id = fields.Many2one(
        "product.pricelist",
        string="Pricelist",
        help="Define pricelist for price computation, "
        "keep empty to take configuration from the backend",
    )

    def _get_pricelist(self):
        self.ensure_one()
        return self.pricelist_id or self.backend_id.pricelist_id
