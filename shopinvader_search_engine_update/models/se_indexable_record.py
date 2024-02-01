# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class SeIndexableRecord(models.AbstractModel):

    _inherit = "se.indexable.record"

    def shopinvader_mark_to_update(self):
        """This method is called in the context of shopinvader to mark a binding
        linked to this record to be updated in the search engine.

        """
        self.sudo().filtered("active")._se_mark_to_update()
