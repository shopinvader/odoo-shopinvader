# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class SeIndexableRecord(models.AbstractModel):

    _inherit = "se.indexable.record"

    def _filter_by_index(self):
        index_id = self.env.context.get("index_id", False)
        records = self
        if index_id:
            records = records.filtered(
                lambda rec, index_id=index_id: index_id
                in rec.se_binding_ids.mapped("index_id").ids
            )
        return records
