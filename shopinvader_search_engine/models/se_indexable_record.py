# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class SeIndexableRecord(models.AbstractModel):

    _inherit = "se.indexable.record"

    def _filter_by_index(self):
        index = self._context.get("index", False)
        records = self
        if index:
            records = records.filtered(
                lambda rec, index=index: index in rec.se_binding_ids.mapped("index_id")
            )
        return records
