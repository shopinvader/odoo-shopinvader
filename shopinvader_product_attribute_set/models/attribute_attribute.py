# Copyright 2021 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AttributeAttribute(models.Model):
    _inherit = "attribute.attribute"

    export_name = fields.Char(compute="_compute_export_name")

    def _compute__export_name(self):
        for rec in self:
            if rec.name.startswith("x_"):
                rec.export_name = rec.name[2:]
            else:
                rec.export_name = rec.name
