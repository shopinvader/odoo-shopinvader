# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SeIndex(models.Model):

    _inherit = "se.index"

    pricelist_ids = fields.Many2many(
        comodel_name="product.pricelist",
        string="Pricelists",
        help="Define pricelists for price computation, "
        "keep empty to take configuration from the backend",
    )

    def _get_pricelists(self):
        self.ensure_one()
        return self.pricelist_ids or self.backend_id.pricelist_ids
