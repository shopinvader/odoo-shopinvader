# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SeasonalConfigLine(models.Model):
    _inherit = "seasonal.config.line"

    shopinvader_bind_ids = fields.One2many(
        "shopinvader.seasonal.config.line",
        "record_id",
        string="Shopinvader Binding",
        context={"active_test": False},
    )
    active = fields.Boolean(default=True, inverse="_inverse_active")

    def _inverse_active(self):
        brands = self.filtered(lambda p: not p.active)
        brands.mapped("shopinvader_bind_ids").write({"active": False})
