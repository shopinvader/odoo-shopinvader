# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SeBackend(models.Model):
    _inherit = "se.backend"

    sale_profile_ids = fields.One2many(
        "shopinvader.sale.profile", "backend_id", "Customer sale profiles"
    )

    def _get_default_profile(self):
        self.ensure_one()
        return fields.first(self.sale_profile_ids.filtered("default"))
