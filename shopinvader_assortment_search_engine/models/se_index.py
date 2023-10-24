# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SeIndex(models.Model):

    _inherit = "se.index"

    @api.model
    def recompute_all_index(self, domain=None):
        self.env["shopinvader.backend"].autobind_product_from_assortment()
        return super().recompute_all_index(domain=domain)
