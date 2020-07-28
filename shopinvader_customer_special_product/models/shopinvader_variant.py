# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models
from odoo.addons.base_sparse_field.models.fields import Serialized


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    procured_for_partners = Serialized(
        compute="_compute_procured_for_partners"
    )

    def _compute_procured_for_partners(self):
        for record in self:
            record.procured_for_partners = record.procured_for_partner_ids.ids
