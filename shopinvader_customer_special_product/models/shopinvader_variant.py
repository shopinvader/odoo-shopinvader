# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models
from odoo.addons.base_sparse_field.models.fields import Serialized


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    export_manufactured_for_partner_ids = Serialized(compute="_compute_export_manufactured_for_partner_ids")

    def _compute_export_manufactured_for_partner_ids(self):
        for record in self:
            if record.manufactured_for_partner_ids:
                record.export_manufactured_for_partner_ids = record.manufactured_for_partner_ids.ids
            else:
                record.export_manufactured_for_partner_ids = False
