# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrExportsLine(models.Model):
    _inherit = "ir.exports.line"

    # Allow to turn on/off index data for products and categories
    active = fields.Boolean(string="Active", default=True)
