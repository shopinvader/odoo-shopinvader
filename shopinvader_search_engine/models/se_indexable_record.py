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

    def _filter_by_bound_in_same_lang(self):
        """
        This methods will fiter the records to only keep the ones that are bound
        to the same lang as the current one for the current index backend.
        :return: recordset
        """
        records = self
        index_id = self.env.context.get("index_id", False)
        if index_id:
            index = self.env["se.index"].browse(index_id)
            lang_id = index.lang_id
            all_index_same_lang = index.backend_id.index_ids.filtered(
                lambda idx, lang=lang_id: idx.lang_id == lang
            )
            valid_indexes = set(all_index_same_lang.ids)
            records = records.filtered(
                lambda rec, valid_indexes=valid_indexes: valid_indexes.intersection(
                    set(rec.se_binding_ids.mapped("index_id").ids)
                )
            )
        return records
