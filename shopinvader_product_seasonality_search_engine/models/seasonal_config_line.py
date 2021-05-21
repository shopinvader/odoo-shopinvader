# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SeasonalConfigLine(models.Model):
    _inherit = "seasonal.config.line"

    def unlink(self):
        # Explicitly call unlink on bindings
        # otherwise the ondelete cascade on record_id will prevail
        # and records will get deleted w/out validation from se.binding.unlink.
        self.shopinvader_bind_ids.unlink()
        return super().unlink()
